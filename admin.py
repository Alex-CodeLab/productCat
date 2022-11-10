from typing import Any

from django.contrib import admin
from django import forms
from django.db import models
from products.models import Product
import json
from flat_json_widget.widgets import FlatJsonWidget

class ProductAdminForm(forms.ModelForm):
    attributes = forms.JSONField(widget=FlatJsonWidget)

    class Meta:
        model = Product
        fields = ('name','attributes')


def get_all_prod_attributes() -> dict[str, Any]:
    attrs = Product.objects.values('attrs').distinct()
    attributes = [attr['attrs'] for attr in attrs]
    att = {}
    for a in attributes:
        for k, v in a.items():
            if k not in att:
                att[k] = [v]
            elif v not in att[k]:
                att[k].append(v)
    return att


def lookups(self, request, model_admin):
    return ((value, value) for value in self.all_attributes[self.title])


def queryset(self, request, queryset):
    for value in self.all_attributes[self.title]:
        if self.value() == value:
            kwargs = {f'attrs__{self.title}_CHAR': value}
            return queryset.filter(**kwargs)


class AttributesFilter(admin.SimpleListFilter):
    all_attributes = get_all_prod_attributes()


# dynamically create AdminFilter classes
filters = [type(f"AttributesFilter{k}", (AttributesFilter,), {
    'title': k,
    'parameter_name': k,
    'lookups': lookups,
    'queryset': queryset})
           for k, v in get_all_prod_attributes().items()]


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'attrs')
    list_filter = [*filters]

    def save_model(self, request, obj, form, change):
        obj.attrs = json.loads(form.data.get('attributes'))
        super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)
