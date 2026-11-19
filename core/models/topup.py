# FASE 2
# Paket top-up: uang asli -> currency game. Tidak linear karena ada bonus, makanya bukan kurs.
#
# Yang dikerjakan:
# - Dataclass TopUpPackage (frozen, slots):
#   price: Money (currency harus kind REAL), grants: Currency (currency game yang didapat),
#   base_amount: int, bonus_amount: int (bonus tetap tiap beli), first_purchase_bonus: int = 0
#   (bonus tambahan yang hanya didapat pada pembelian pertama paket ini).
# - Property total_amount: base_amount + bonus_amount (tanpa bonus pembelian pertama).
# - Property first_purchase_total: total_amount + first_purchase_bonus.
# - Validasi: price > 0, semua jumlah >= 0, base_amount > 0.
#
# Jangan: menaruh logika pencarian paket termurah di sini (itu tugas core/topup_optimizer.py).
