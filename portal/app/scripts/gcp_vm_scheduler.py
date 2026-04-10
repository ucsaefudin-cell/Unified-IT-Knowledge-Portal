"""
Modul gcp_vm_scheduler.py -- FinOps Automation Script
Unified IT Knowledge Portal -- GCP Cloud Function

Tujuan:
    Menjadwalkan start/stop Compute Engine VM secara otomatis
    untuk menghemat biaya cloud di luar jam operasional.

    Jadwal yang direkomendasikan (via Cloud Scheduler):
    - START : Setiap hari pukul 07:00 WIB (00:00 UTC)
    - STOP  : Setiap hari pukul 19:00 WIB (12:00 UTC)

    Estimasi penghematan: VM hanya berjalan 12 jam/hari (50% dari 24 jam)
    = penghematan ~50% biaya Compute Engine per bulan.

Cara deploy:
    Lihat docstring fungsi cloud_function_entry_point() di bawah.

Dependensi (requirements.txt untuk Cloud Function):
    google-cloud-compute==1.19.2
    functions-framework==3.8.1

Prinsip Clean Code (Task 0):
    - PEP 8: indentasi 4 spasi, max 79 karakter per baris
    - DRY: logika start/stop diekstrak ke fungsi terpisah
    - Nama deskriptif: tidak ada variabel ambigu
    - Semua docstring dan komentar dalam Bahasa Indonesia
"""

import json
import logging
import os
from datetime import datetime, timezone

import functions_framework
from google.cloud import compute_v1
from google.api_core.exceptions import GoogleAPICallError, NotFound


# ============================================================
# KONFIGURASI LOGGING
# Menggunakan format standar dengan timestamp, level, dan pesan
# agar mudah dianalisis di GCP Cloud Logging (Stackdriver)
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S UTC",
)

# Buat logger khusus untuk modul ini
logger = logging.getLogger("gcp_vm_scheduler")


# ============================================================
# KONSTANTA -- Nilai tetap untuk validasi dan status VM
# ============================================================

# Aksi yang didukung oleh scheduler ini
SUPPORTED_ACTIONS = frozenset({"start", "stop"})

# Status VM GCP yang mungkin dikembalikan oleh Compute Engine API
VM_STATUS_RUNNING = "RUNNING"
VM_STATUS_TERMINATED = "TERMINATED"
VM_STATUS_STOPPED = "STOPPED"
VM_STATUS_STAGING = "STAGING"
VM_STATUS_STOPPING = "STOPPING"

# Status yang dianggap "sudah berjalan" -- tidak perlu start lagi
VM_STATUSES_CONSIDERED_RUNNING = frozenset({
    VM_STATUS_RUNNING,
    VM_STATUS_STAGING,
})

# Status yang dianggap "sudah berhenti" -- tidak perlu stop lagi
VM_STATUSES_CONSIDERED_STOPPED = frozenset({
    VM_STATUS_TERMINATED,
    VM_STATUS_STOPPED,
})


# ============================================================
# FUNGSI PRIVAT -- Logika inti scheduler
# ============================================================

def _extract_scheduler_payload(cloud_event_data: dict) -> dict:
    """
    Ekstrak dan validasi payload dari Cloud Scheduler event.

    Cloud Scheduler mengirim data sebagai JSON string yang di-encode
    dalam field 'data' dari Cloud Event. Fungsi ini mendekode dan
    memvalidasi semua field yang diperlukan.

    Format payload yang diharapkan (JSON):
    {
        "action"      : "start" atau "stop",
        "project_id"  : "nama-project-gcp-anda",
        "zone"        : "asia-southeast2-a",
        "instance_id" : "nama-vm-instance"
    }

    Args:
        cloud_event_data: Dict data dari Cloud Event yang diterima.

    Returns:
        Dict berisi action, project_id, zone, dan instance_id yang sudah
        divalidasi dan dibersihkan.

    Raises:
        ValueError: Jika payload tidak valid atau field wajib tidak ada.
    """
    # Decode payload -- Cloud Scheduler mengirim data sebagai bytes atau string
    raw_payload = cloud_event_data.get("data", "{}")

    if isinstance(raw_payload, bytes):
        # Decode bytes ke string UTF-8 terlebih dahulu
        decoded_payload_string = raw_payload.decode("utf-8")
    else:
        decoded_payload_string = str(raw_payload)

    # Parse JSON string menjadi dict Python
    try:
        payload_dict = json.loads(decoded_payload_string)
    except json.JSONDecodeError as json_error:
        raise ValueError(
            f"Payload bukan JSON yang valid: {json_error}"
        ) from json_error

    # Validasi field wajib -- semua harus ada dan tidak boleh kosong
    required_fields = ["action", "project_id", "zone", "instance_id"]
    missing_fields = [
        field for field in required_fields
        if not payload_dict.get(field)
    ]

    if missing_fields:
        raise ValueError(
            f"Field wajib tidak ditemukan dalam payload: {missing_fields}"
        )

    # Normalisasi action ke lowercase untuk konsistensi
    normalized_action = payload_dict["action"].strip().lower()

    # Validasi nilai action -- hanya 'start' atau 'stop' yang diizinkan
    if normalized_action not in SUPPORTED_ACTIONS:
        raise ValueError(
            f"Aksi tidak valid: '{normalized_action}'. "
            f"Gunakan salah satu dari: {sorted(SUPPORTED_ACTIONS)}"
        )

    return {
        "action": normalized_action,
        "project_id": payload_dict["project_id"].strip(),
        "zone": payload_dict["zone"].strip(),
        "instance_id": payload_dict["instance_id"].strip(),
    }


def _get_current_vm_status(
    compute_client: compute_v1.InstancesClient,
    project_id: str,
    zone: str,
    instance_id: str,
) -> str:
    """
    Ambil status terkini VM dari GCP Compute Engine API.

    Status yang mungkin dikembalikan:
    - RUNNING    : VM sedang berjalan
    - STAGING    : VM sedang dalam proses start
    - STOPPING   : VM sedang dalam proses stop
    - TERMINATED : VM sudah berhenti (dihentikan oleh user/scheduler)
    - STOPPED    : VM sudah berhenti (dihentikan oleh GCP)
    - SUSPENDED  : VM dalam kondisi suspend

    Args:
        compute_client: Instance Compute Engine API client.
        project_id: ID project GCP tempat VM berada.
        zone: Zona GCP tempat VM berada (contoh: 'asia-southeast2-a').
        instance_id: Nama instance VM yang akan dicek.

    Returns:
        String status VM dalam huruf kapital (contoh: 'RUNNING').

    Raises:
        NotFound: Jika VM dengan nama tersebut tidak ditemukan.
        GoogleAPICallError: Jika terjadi error saat memanggil GCP API.
    """
    logger.info(
        "Mengambil status VM | project=%s | zone=%s | instance=%s",
        project_id, zone, instance_id
    )

    # Panggil GCP Compute Engine API untuk mendapatkan detail instance
    vm_instance = compute_client.get(
        project=project_id,
        zone=zone,
        instance=instance_id,
    )

    current_status = vm_instance.status
    logger.info(
        "Status VM saat ini: %s | instance=%s",
        current_status, instance_id
    )

    return current_status


def _start_vm_instance(
    compute_client: compute_v1.InstancesClient,
    project_id: str,
    zone: str,
    instance_id: str,
    current_vm_status: str,
) -> dict:
    """
    Jalankan VM jika belum dalam status RUNNING.

    Menerapkan prinsip IDEMPOTENCY:
    Jika VM sudah RUNNING atau STAGING, fungsi ini TIDAK akan
    mengirim perintah start ke API -- hanya mencatat log dan kembali.
    Ini mencegah error dan biaya tidak perlu akibat perintah ganda.

    Args:
        compute_client: Instance Compute Engine API client.
        project_id: ID project GCP.
        zone: Zona GCP tempat VM berada.
        instance_id: Nama instance VM yang akan distart.
        current_vm_status: Status VM saat ini (dari _get_current_vm_status).

    Returns:
        Dict berisi 'action', 'instance_id', 'status_before',
        'result', dan 'timestamp' untuk keperluan logging FinOps.
    """
    execution_timestamp = datetime.now(timezone.utc).isoformat()

    # IDEMPOTENCY CHECK: Jangan start jika VM sudah berjalan
    if current_vm_status in VM_STATUSES_CONSIDERED_RUNNING:
        logger.warning(
            "IDEMPOTENCY: VM sudah dalam status '%s'. "
            "Perintah START diabaikan. | instance=%s",
            current_vm_status, instance_id
        )
        return {
            "action": "start",
            "instance_id": instance_id,
            "status_before": current_vm_status,
            "result": "SKIPPED -- VM sudah berjalan",
            "timestamp": execution_timestamp,
        }

    # Kirim perintah START ke GCP Compute Engine API
    logger.info(
        "Mengirim perintah START | instance=%s | status_sebelum=%s",
        instance_id, current_vm_status
    )

    start_operation = compute_client.start(
        project=project_id,
        zone=zone,
        instance=instance_id,
    )

    # Tunggu operasi selesai (blocking call)
    start_operation.result()

    logger.info(
        "VM berhasil DISTART | instance=%s | timestamp=%s",
        instance_id, execution_timestamp
    )

    return {
        "action": "start",
        "instance_id": instance_id,
        "status_before": current_vm_status,
        "result": "SUCCESS -- VM berhasil distart",
        "timestamp": execution_timestamp,
    }


def _stop_vm_instance(
    compute_client: compute_v1.InstancesClient,
    project_id: str,
    zone: str,
    instance_id: str,
    current_vm_status: str,
) -> dict:
    """
    Hentikan VM jika belum dalam status TERMINATED atau STOPPED.

    Menerapkan prinsip IDEMPOTENCY:
    Jika VM sudah TERMINATED atau STOPPED, fungsi ini TIDAK akan
    mengirim perintah stop ke API -- hanya mencatat log dan kembali.

    Args:
        compute_client: Instance Compute Engine API client.
        project_id: ID project GCP.
        zone: Zona GCP tempat VM berada.
        instance_id: Nama instance VM yang akan dihentikan.
        current_vm_status: Status VM saat ini.

    Returns:
        Dict berisi 'action', 'instance_id', 'status_before',
        'result', dan 'timestamp' untuk keperluan logging FinOps.
    """
    execution_timestamp = datetime.now(timezone.utc).isoformat()

    # IDEMPOTENCY CHECK: Jangan stop jika VM sudah berhenti
    if current_vm_status in VM_STATUSES_CONSIDERED_STOPPED:
        logger.warning(
            "IDEMPOTENCY: VM sudah dalam status '%s'. "
            "Perintah STOP diabaikan. | instance=%s",
            current_vm_status, instance_id
        )
        return {
            "action": "stop",
            "instance_id": instance_id,
            "status_before": current_vm_status,
            "result": "SKIPPED -- VM sudah berhenti",
            "timestamp": execution_timestamp,
        }

    # Kirim perintah STOP ke GCP Compute Engine API
    logger.info(
        "Mengirim perintah STOP | instance=%s | status_sebelum=%s",
        instance_id, current_vm_status
    )

    stop_operation = compute_client.stop(
        project=project_id,
        zone=zone,
        instance=instance_id,
    )

    # Tunggu operasi selesai (blocking call)
    stop_operation.result()

    logger.info(
        "VM berhasil DIHENTIKAN | instance=%s | timestamp=%s",
        instance_id, execution_timestamp
    )

    return {
        "action": "stop",
        "instance_id": instance_id,
        "status_before": current_vm_status,
        "result": "SUCCESS -- VM berhasil dihentikan",
        "timestamp": execution_timestamp,
    }


def _log_finops_summary(execution_result: dict) -> None:
    """
    Catat ringkasan eksekusi untuk keperluan FinOps tracking.

    Log ini akan muncul di GCP Cloud Logging dan dapat digunakan
    untuk membuat dashboard penghematan biaya di Looker Studio.

    Format log yang dihasilkan:
    [FINOPS] action=stop | instance=my-vm | result=SUCCESS | ts=2026-04-10T19:00:00+00:00

    Args:
        execution_result: Dict hasil eksekusi dari _start_vm_instance
                          atau _stop_vm_instance.
    """
    logger.info(
        "[FINOPS] action=%s | instance=%s | result=%s | ts=%s",
        execution_result.get("action", "unknown"),
        execution_result.get("instance_id", "unknown"),
        execution_result.get("result", "unknown"),
        execution_result.get("timestamp", "unknown"),
    )


# ============================================================
# ENTRY POINT -- Fungsi utama yang dipanggil oleh Cloud Functions
# ============================================================

@functions_framework.cloud_event
def cloud_function_entry_point(cloud_event):
    """
    Entry point utama untuk GCP Cloud Function.

    Fungsi ini dipanggil secara otomatis oleh GCP Cloud Functions
    setiap kali Cloud Scheduler mengirim trigger sesuai jadwal.

    Decorator @functions_framework.cloud_event menandai fungsi ini
    sebagai handler untuk CloudEvents (format standar event GCP).

    Alur eksekusi:
    1. Ekstrak dan validasi payload dari Cloud Event
    2. Buat Compute Engine API client
    3. Ambil status VM terkini
    4. Jalankan aksi START atau STOP (dengan idempotency check)
    5. Catat hasil ke log untuk FinOps tracking

    Cara deploy ke GCP Cloud Functions:
    -----------------------------------------------
    1. Buat folder deployment:
       mkdir gcp_scheduler && cd gcp_scheduler
       cp gcp_vm_scheduler.py main.py

    2. Buat requirements.txt:
       echo "google-cloud-compute==1.19.2" > requirements.txt
       echo "functions-framework==3.8.1" >> requirements.txt

    3. Deploy via gcloud CLI:
       gcloud functions deploy vm-scheduler \\
         --gen2 \\
         --runtime=python312 \\
         --region=asia-southeast2 \\
         --source=. \\
         --entry-point=cloud_function_entry_point \\
         --trigger-topic=vm-scheduler-topic \\
         --service-account=vm-scheduler-sa@PROJECT_ID.iam.gserviceaccount.com

    4. Buat Cloud Scheduler jobs:
       # Job START -- setiap hari pukul 07:00 WIB (00:00 UTC)
       gcloud scheduler jobs create pubsub start-vm-job \\
         --schedule="0 0 * * *" \\
         --topic=vm-scheduler-topic \\
         --message-body='{"action":"start","project_id":"PROJECT_ID","zone":"asia-southeast2-a","instance_id":"INSTANCE_NAME"}' \\
         --time-zone="Asia/Jakarta"

       # Job STOP -- setiap hari pukul 19:00 WIB (12:00 UTC)
       gcloud scheduler jobs create pubsub stop-vm-job \\
         --schedule="0 12 * * *" \\
         --topic=vm-scheduler-topic \\
         --message-body='{"action":"stop","project_id":"PROJECT_ID","zone":"asia-southeast2-a","instance_id":"INSTANCE_NAME"}' \\
         --time-zone="Asia/Jakarta"

    5. Buat Service Account dengan permission minimal:
       gcloud iam service-accounts create vm-scheduler-sa \\
         --display-name="VM Scheduler Service Account"
       gcloud projects add-iam-policy-binding PROJECT_ID \\
         --member="serviceAccount:vm-scheduler-sa@PROJECT_ID.iam.gserviceaccount.com" \\
         --role="roles/compute.instanceAdmin.v1"

    Args:
        cloud_event: CloudEvent object yang dikirim oleh Cloud Scheduler
                     via Pub/Sub. Berisi data payload dalam format JSON.
    """
    logger.info(
        "=== GCP VM Scheduler diaktifkan | event_id=%s ===",
        cloud_event.get("id", "unknown")
    )

    # --- Langkah 1: Ekstrak dan validasi payload ---
    try:
        scheduler_payload = _extract_scheduler_payload(
            cloud_event.data or {}
        )
    except ValueError as validation_error:
        logger.error(
            "Payload tidak valid: %s", validation_error
        )
        # Kembalikan tanpa raise agar Cloud Functions tidak retry
        # (payload yang salah tidak akan menjadi benar dengan retry)
        return

    requested_action = scheduler_payload["action"]
    target_project_id = scheduler_payload["project_id"]
    target_zone = scheduler_payload["zone"]
    target_instance_id = scheduler_payload["instance_id"]

    logger.info(
        "Payload diterima | action=%s | project=%s | zone=%s | instance=%s",
        requested_action, target_project_id, target_zone, target_instance_id
    )

    # --- Langkah 2: Buat Compute Engine API client ---
    # Client otomatis menggunakan Application Default Credentials (ADC)
    # dari Service Account yang di-attach ke Cloud Function
    compute_api_client = compute_v1.InstancesClient()

    # --- Langkah 3: Ambil status VM terkini ---
    try:
        current_vm_status = _get_current_vm_status(
            compute_client=compute_api_client,
            project_id=target_project_id,
            zone=target_zone,
            instance_id=target_instance_id,
        )
    except NotFound:
        logger.error(
            "VM tidak ditemukan | project=%s | zone=%s | instance=%s",
            target_project_id, target_zone, target_instance_id
        )
        return
    except GoogleAPICallError as api_error:
        logger.error(
            "Error saat mengambil status VM: %s", api_error
        )
        raise  # Re-raise agar Cloud Functions melakukan retry

    # --- Langkah 4: Eksekusi aksi START atau STOP ---
    try:
        if requested_action == "start":
            execution_result = _start_vm_instance(
                compute_client=compute_api_client,
                project_id=target_project_id,
                zone=target_zone,
                instance_id=target_instance_id,
                current_vm_status=current_vm_status,
            )
        else:
            # requested_action == "stop" (sudah divalidasi sebelumnya)
            execution_result = _stop_vm_instance(
                compute_client=compute_api_client,
                project_id=target_project_id,
                zone=target_zone,
                instance_id=target_instance_id,
                current_vm_status=current_vm_status,
            )
    except GoogleAPICallError as api_error:
        logger.error(
            "Error saat mengeksekusi aksi '%s' pada VM '%s': %s",
            requested_action, target_instance_id, api_error
        )
        raise  # Re-raise agar Cloud Functions melakukan retry

    # --- Langkah 5: Catat ringkasan FinOps ---
    _log_finops_summary(execution_result)

    logger.info(
        "=== Scheduler selesai | action=%s | instance=%s ===",
        requested_action, target_instance_id
    )
