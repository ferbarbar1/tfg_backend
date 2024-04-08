from django.contrib import admin
from .models import Owner, Worker, Client


class OwnerAdmin(admin.ModelAdmin):
    pass


class WorkerAdmin(admin.ModelAdmin):
    pass


class ClientAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(Owner, OwnerAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Client, ClientAdmin)
