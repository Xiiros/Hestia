"""Tutoriels de désactivation du DHCP, par box.

⚠️ Les étapes ci-dessous sont des **modèles** : les libellés exacts varient selon
le modèle de box et la version du firmware. À valider et illustrer (captures
d'écran) avec du vrai matériel avant mise en production. Le tutoriel générique
sert de repli et fonctionne quelle que soit la box.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hestia.system.vendors import Isp


@dataclass(slots=True, frozen=True)
class Tutorial:
    box_name: str
    admin_url: str
    steps: list[str] = field(default_factory=list)
    note: str = ""


_TUTORIALS: dict[Isp, Tutorial] = {
    Isp.ORANGE: Tutorial(
        box_name="Livebox (Orange)",
        admin_url="http://192.168.1.1",
        steps=[
            "Ouvrez http://192.168.1.1 dans un navigateur.",
            "Connectez-vous (mot de passe au dos de la Livebox).",
            "Allez dans « Réseau » puis « DHCP ».",
            "Passez le serveur DHCP sur « Désactivé ».",
            "Enregistrez, puis redémarrez la Livebox.",
        ],
        note="Sur certaines Livebox, le réglage est sous « Configuration avancée ».",
    ),
    Isp.FREE: Tutorial(
        box_name="Freebox (Free)",
        admin_url="http://mafreebox.freebox.fr",
        steps=[
            "Ouvrez http://mafreebox.freebox.fr.",
            "Connectez-vous à l'interface Freebox OS.",
            "Ouvrez « Paramètres de la Freebox » puis « DHCP ».",
            "Décochez « Activer le serveur DHCP ».",
            "Cliquez sur « Sauvegarder ».",
        ],
        note="La Freebox peut demander une validation physique sur le boîtier.",
    ),
    Isp.BOUYGUES: Tutorial(
        box_name="Bbox (Bouygues)",
        admin_url="http://192.168.1.254",
        steps=[
            "Ouvrez http://192.168.1.254 (ou http://mabbox.bytel.fr).",
            "Connectez-vous à l'interface d'administration.",
            "Allez dans « Réseau » puis « DHCP ».",
            "Désactivez le serveur DHCP.",
            "Validez et redémarrez la Bbox.",
        ],
    ),
    Isp.SFR: Tutorial(
        box_name="Box SFR",
        admin_url="http://192.168.1.1",
        steps=[
            "Ouvrez http://192.168.1.1.",
            "Connectez-vous (identifiants au dos de la box).",
            "Allez dans « Réseau v4 » puis « DHCP ».",
            "Désactivez le serveur DHCP.",
            "Enregistrez les modifications.",
        ],
    ),
}


def generic_tutorial(admin_url: str) -> Tutorial:
    """Tutoriel de repli, valable pour n'importe quelle box."""

    return Tutorial(
        box_name="votre box Internet",
        admin_url=admin_url,
        steps=[
            f"Ouvrez {admin_url} dans un navigateur.",
            "Connectez-vous (identifiants souvent au dos de la box).",
            "Cherchez la section « Réseau », « LAN » ou « DHCP ».",
            "Désactivez le serveur DHCP.",
            "Enregistrez, puis redémarrez la box si demandé.",
        ],
        note="Les libellés exacts dépendent de votre box.",
    )


def tutorial_for(isp: Isp, admin_url: str) -> Tutorial:
    """Renvoie le tutoriel de la box détectée, ou le tutoriel générique.

    ``admin_url`` (déduit de l'IP du serveur DHCP détecté) alimente le repli
    générique afin d'afficher la bonne adresse même pour une box inconnue.
    """

    return _TUTORIALS.get(isp) or generic_tutorial(admin_url)
