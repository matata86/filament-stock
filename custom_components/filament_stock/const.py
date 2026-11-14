"""Constants for Filament Stock."""

DOMAIN = "filament_stock"
SOURCE_PLATFORM = "bambu_lab"

CONF_PRINTER = "printer_device"
CONF_WASTE = "waste_percent"
CONF_LOW = "low_threshold_g"
CONF_SPOOL = "spool_weight_g"
CONF_AI = "ai_task_entity"  # optional: reads a label photo when a barcode is unknown

DEFAULTS = {CONF_WASTE: 5.0, CONF_LOW: 300.0, CONF_SPOOL: 1000.0}
