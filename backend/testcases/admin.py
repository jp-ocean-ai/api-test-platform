from django.contrib import admin

from .models import TestCase, TestStep


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'api', 'environment', 'default_environment', 'enabled')
    list_filter = ('project', 'enabled')
    search_fields = ('name',)


@admin.register(TestStep)
class TestStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'testcase', 'project', 'order', 'api', 'environment', 'enabled')
    list_filter = ('project', 'enabled', 'continue_on_failure')
    search_fields = ('name',)
