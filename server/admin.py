from django.contrib import admin
from django.utils.html import format_html
from .models import SafeguardReport


@admin.register(SafeguardReport)
class SafeguardReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'machine_serial',
        'engine_off_timestamp',
        'colored_safety',
        'formatted_distance',
        'is_active',
    )

    list_filter = ('is_safe', 'is_active', 'machine_serial')

    search_fields = ('machine_serial',)

    readonly_fields = ('report_datetime',)

    date_hierarchy = 'engine_off_timestamp'

    fieldsets = (
        (' Información Básica', {
            'fields': ('machine_serial', 'report_datetime', 'engine_off_timestamp')
        }),
        (' Ubicación Geográfica', {
            'fields': ('latitude', 'longitude')
        }),
        (' Análisis de Seguridad', {
            'fields': ('distance_to_road_m', 'is_safe')
        }),
        (' Estado del Informe', {
            'fields': ('is_active',)
        }),
    )

    def colored_safety(self, obj):
        color = "#22c55e" if obj.is_safe else "#ef4444" 
        text = "✅ Seguro" if obj.is_safe else "⚠️ Inseguro"
        return format_html('<b style="color:{};">{}</b>', color, text)
    colored_safety.short_description = "Estado de Seguridad"

    def formatted_distance(self, obj):
        return f"{obj.distance_to_road_m:.1f} m"
    formatted_distance.short_description = "Distancia al Camino"

    icon_name = "security"
    ordering = ('-engine_off_timestamp',)
