from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
	list_display = ('id','title','file_type','uploader','uploaded_at')
	search_fields = ('title','description')
	list_filter = ('file_type','uploaded_at')
