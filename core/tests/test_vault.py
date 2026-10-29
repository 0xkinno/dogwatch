import pytest
from nacl.exceptions import CryptoError

from dogwatch.vault import crypto
from dogwatch.vault.identifiers import (DEFAULT_DETECTORS, detect_cdc, detect_coc, detect_coe, detect_email,
                                        detect_indos, detect_passport_number, detect_phone, mrz_check_digit,
                                        parse_mrz_td3)
from dogwatch.vault.placeholders import Found, Registry, replace_identifiers, resolve_overlaps
from dogwatch.vault.store import Vault

L1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
L2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"


def test_icao_sample_check_digits_valid():
    assert mrz_check_digit("L898902C3") == "6"
    info = parse_mrz_td3(L1, L2)
    assert info["valid"] and info["surname"] == "ERIKSSON" and info["given"] == "ANNA MARIA"


def test_invalid_check_digit_detected():
    bad = L2[:9] + "7" + L2[10:]
    info = parse_mrz_td3(L1, bad)
    assert not info["valid"] and not info["checks"]["number"]


def test_mrz_block_redacted_even_when_check_digits_fail():
    bad = L2[:9] + "7" + L2[10:]
    reg = Registry()
    out, found = replace_identifiers(f"scan:\n{L1}\n{bad}\nend", DEFAULT_DETECTORS, reg)
    assert "ERIKSSON" not in out and "L898902C3" not in out
    assert any(f.kind == "MRZ" and not f.verified for f in found)


def test_mrz_valid_marks_verified():
    _, found = replace_identifiers(f"{L1}\n{L2}", DEFAULT_DETECTORS, Registry())
    assert any(f.kind == "MRZ" and f.verified for f in found)


def test_passport_pattern():
    assert [f.value for f in detect_passport_number("No. K1234567 issued")] == ["K1234567"]
    assert detect_passport_number("Z1234567") == []
    assert detect_passport_number("K0234567") == []


def test_labelled_detectors():
    assert detect_coc("CoC No: 123456/MUM/2019 valid")[0].value == "123456/MUM/2019"
    assert detect_indos("INDoS No. 09AB1234")[0].value == "09AB1234"
    assert detect_cdc("CDC Number MUM123456")[0].value == "MUM123456"
    assert detect_coe("CoE No: SG123456")[0].value == "SG123456"
    assert detect_coc("CoC valid until March") == []


def test_email_and_phone_not_dates():
    assert detect_email("write to a.b@ship.example now")[0].value == "a.b@ship.example"
    assert detect_phone("call +91 98765 43210 today")
    assert detect_phone("expires 2027-03-14 and 14/03/2027") == []


def test_placeholders_are_stable_per_value():
    reg = Registry()
    a = reg.assign("coc", "123-456")
    b = reg.assign("COC", "123456")
    c = reg.assign("COC", "999999")
    assert a == b == "[[COC_1]]" and c == "[[COC_2]]"


def test_overlap_keeps_longest():
    kept = resolve_overlaps([Found("A", "abcdef", 0, 6), Found("B", "cd", 2, 4), Found("C", "xy", 8, 10)])
    assert [k.kind for k in kept] == ["A", "C"]


def test_rehydrate_round_trip_and_no_value_in_output():
    reg = Registry()
    text = "CoC No: 123456/MUM/2019 and K1234567"
    out, _ = replace_identifiers(text, DEFAULT_DETECTORS, reg)
    assert "123456" not in out and "K1234567" not in out
    assert reg.rehydrate(out) == text


def test_vault_round_trip_and_wrong_passphrase(tmp_path):
    v = Vault.create(tmp_path / "v", "correct horse")
    v.registry.assign("COC", "123456")
    v.save_registry()
    v.put_documents([{"id": "coc"}])
    v.add_ledger_entry({"sign_on": "2026-01-01"})
    cid = v.add_image(b"\x89PNGdata")
    v2 = Vault.open(tmp_path / "v", "correct horse")
    assert v2.documents() == [{"id": "coc"}] and v2.ledger()[0]["sign_on"] == "2026-01-01"
    assert v2.registry.rehydrate("[[COC_1]]") == "123456"
    assert v2.read_image(cid) == b"\x89PNGdata"
    with pytest.raises(CryptoError):
        Vault.open(tmp_path / "v", "wrong")


def test_vault_files_hold_no_plaintext(tmp_path):
    v = Vault.create(tmp_path / "v", "pw")
    v.registry.assign("PASSPORT", "K1234567")
    v.save_registry()
    blob = b"".join(p.read_bytes() for p in (tmp_path / "v").rglob("*") if p.is_file())
    assert b"K1234567" not in blob


def test_tamper_detected():
    key = crypto.derive_key("x", b"0" * 16)
    blob = bytearray(crypto.encrypt(key, b"hello"))
    blob[-1] ^= 1
    with pytest.raises(CryptoError):
        crypto.decrypt(key, bytes(blob))
