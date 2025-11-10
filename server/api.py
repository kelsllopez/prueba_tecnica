from ninja import Router
from ninja.responses import Response
from django.shortcuts import get_object_or_404
from .models import SafeguardReport
from .services import process_files
from .schemas import SafeguardReportOut, ProcessingResponseSchema, UpdateActiveSchema

router = Router()

@router.post("/data-processing/", response=ProcessingResponseSchema)
def process_data(request):

    created = process_files()
    message = f"Data processing completed successfully. {created} reports created."
    return Response({"message": message}, status=202)


@router.get("/safeguard-reports/", response=list[SafeguardReportOut])
def list_reports(request):
    reports = SafeguardReport.objects.filter(is_active=True).order_by("id")
    result = []
    for r in reports:
        result.append({
            "id": r.id,
            "machine_serial": r.machine_serial or "844585",
            "report_datetime": r.report_datetime,
            "engine_off_timestamp": r.engine_off_timestamp,
            "is_safe": r.is_safe,
            "location": {
                "latitude": r.latitude,
                "longitude": r.longitude,
            },
            "distance_to_road_m": round(r.distance_to_road_m, 2),
            "is_active": r.is_active,
        })
    return result



@router.patch("/safeguard-reports/{id}/", response=ProcessingResponseSchema)
def update_report_status(request, id: int, payload: UpdateActiveSchema):

    report = get_object_or_404(SafeguardReport, id=id)
    report.is_active = payload.is_active
    report.save()
    
    return {"message": f"Report {id} updated successfully."}
