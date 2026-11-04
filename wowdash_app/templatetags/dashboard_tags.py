from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def trend_indicator(trend_value, trend_abs_value, label=""):
    """
    Creates a trend indicator with up/down arrow and value.
    
    Args:
        trend_value: The actual trend value (positive or negative)
        trend_abs_value: The absolute value of the trend
        label: Optional label to display after the trend value
    
    Returns:
        HTML string with the trend indicator
    """
    if trend_value > 0:
        html = f'''
            <span class="inline-flex items-center gap-1 text-success-600 dark:text-success-400">
                <iconify-icon icon="bxs:up-arrow" class="text-xs"></iconify-icon> {trend_abs_value}
            </span>
        '''
    else:
        html = f'''
            <span class="inline-flex items-center gap-1 text-danger-600 dark:text-danger-400">
                <iconify-icon icon="bxs:down-arrow" class="text-xs"></iconify-icon> {trend_abs_value}
            </span>
        '''
    
    if label:
        html += f' {label}'
        
    return mark_safe(html) 