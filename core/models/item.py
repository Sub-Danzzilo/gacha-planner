# FASE 1 (gambar: FASE 5)
# Item yang bisa didapat dari banner.
#
# Yang dikerjakan:
# - Dataclass Item (frozen, slots): name: str, tier_name: str, is_featured: bool = False,
#   image_path: Path | None = None.
#   Validasi: name tidak kosong setelah strip.
#   image_path disimpan relatif terhadap folder profil, bukan path absolut, supaya profil bisa dipindah.
#
# Jangan: memuat gambar atau mengimpor Pillow di sini. Pemuatan gambar urusan ui/ (fase 5).
