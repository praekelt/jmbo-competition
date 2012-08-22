from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag(
    'competition/inclusion_tags/competition_detail.html',
    takes_context=True
)

def competition_detail(context, obj):
    can_enter, reason = obj.can_enter(context['request'])
    print can_enter
    print reason
    context.update({
        'object': obj,
        'can_enter': can_enter,
        'reason': reason
        })  
    return context