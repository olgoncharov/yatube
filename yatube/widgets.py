from django import forms


class ImageWidget(forms.ClearableFileInput):
    template_name = 'django/forms/widgets/image_input.html'

    def __init__(self, attrs=None, width=200, height=200, role='picture'):
        self.width = width
        self.height = height
        self.role = role
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'width': self.width,
            'height': self.height,
            'role': self.role,
        })
        return context
