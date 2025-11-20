from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def def_goups(sender, **kwargs):
    grupos = [
        'Funcionario',
        'Jefatura',
        'Subdireccion Administrativa',
        'Subdireccion Clinica',
        'Direccion'
    ]

    for nombre in grupos:
        Group.objects.get_or_create(name = nombre)