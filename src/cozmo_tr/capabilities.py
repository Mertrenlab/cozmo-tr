"""Publish honest status for user-visible Cozmo capabilities.

Responsible for: stable IDs, Turkish labels, commands, and verification state.
Not responsible for: feature execution or hardware probing.
"""

from dataclasses import asdict, dataclass
from enum import StrEnum


class CapabilityState(StrEnum):
    """Distinguish verified software from experiments and missing hardware."""

    READY = "ready"
    EXPERIMENTAL = "experimental"
    HARDWARE_PENDING = "hardware_pending"


@dataclass(frozen=True, slots=True)
class Capability:
    """Describe one cohesive feature group and its spoken examples."""

    id: str
    label: str
    state: CapabilityState
    commands: tuple[str, ...]
    note: str


CAPABILITIES: tuple[Capability, ...] = (
    Capability(
        "motion",
        "Hareket",
        CapabilityState.EXPERIMENTAL,
        ("ileri 50", "geri 30", "sola 45", "sağa 45", "dur"),
        "Zemin smoke testi gerekli.",
    ),
    Capability(
        "speech",
        "Türkçe konuşma",
        CapabilityState.EXPERIMENTAL,
        ("söyle merhaba", "nasılsın", "adın ne", "şaka yap"),
        "Cozmo hoparlörüne yerel WAV gönderir.",
    ),
    Capability(
        "head_lift",
        "Baş ve kol",
        CapabilityState.EXPERIMENTAL,
        ("başını kaldır", "başını indir", "kolunu kaldır", "kolunu indir"),
        "Doğrudan motor hedefleri sınırlıdır.",
    ),
    Capability(
        "lights",
        "Işıklar",
        CapabilityState.EXPERIMENTAL,
        ("ışıklarını kırmızı yap", "ışıkları kapat", "kafa ışığını aç"),
        "Sırt ve kafa ışığını kontrol eder.",
    ),
    Capability(
        "face",
        "OLED ifadeleri",
        CapabilityState.EXPERIMENTAL,
        ("mutlu ol", "üzgün ol", "şaşır", "kızgın ol"),
        "Haricî animasyon arşivi kullanmaz.",
    ),
    Capability(
        "camera",
        "Fotoğraf",
        CapabilityState.EXPERIMENTAL,
        ("fotoğraf çek",),
        "Açık komutla tek yerel kare kaydeder.",
    ),
    Capability(
        "status",
        "Pil ve ses",
        CapabilityState.EXPERIMENTAL,
        ("pilin ne kadar", "sesini kıs", "sesini aç"),
        "Pil voltajını söyler ve ses seviyesini ayarlar.",
    ),
    Capability(
        "gestures",
        "Hareket rutinleri",
        CapabilityState.EXPERIMENTAL,
        ("selam ver", "dans et", "kafanı salla", "görüşürüz"),
        "Sonlu güvenli ilkelere açılır.",
    ),
    Capability(
        "ball_play",
        "Top oyunu",
        CapabilityState.HARDWARE_PENDING,
        ("topu bul", "topla oyna"),
        "Algılayıcı sentetik testli; gerçek top smoke testi bekliyor.",
    ),
    Capability(
        "cubes",
        "Işıklı küpler",
        CapabilityState.HARDWARE_PENDING,
        ("kaç küp var", "küpü kırmızı yak", "küp ışıklarını kapat"),
        "Üç küp türünü bulur; BLE bağlantısı ve LED smoke testi bekliyor.",
    ),
    Capability(
        "charger",
        "Şarj istasyonu ışıkları",
        CapabilityState.HARDWARE_PENDING,
        ("şarj ışığını mavi yak", "şarj ışığını kapat"),
        "İstasyonun üç LED'ini kontrol eder; fiziksel smoke testi bekliyor.",
    ),
)


def capability_by_id(capability_id: str) -> Capability:
    """Return one stable capability or raise KeyError for an unknown ID."""
    for capability in CAPABILITIES:
        if capability.id == capability_id:
            return capability
    raise KeyError(capability_id)


def command_lines() -> tuple[str, ...]:
    """Render concise Turkish command groups with verification states."""
    return tuple(
        f"[{item.state.value}] {item.label}: {', '.join(item.commands)}"
        for item in CAPABILITIES
    )


def capability_payloads() -> list[dict[str, object]]:
    """Return JSON-ready catalog values without mutating the registry."""
    return [asdict(item) for item in CAPABILITIES]
