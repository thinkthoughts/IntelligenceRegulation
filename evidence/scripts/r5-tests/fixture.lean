/- Test fixture for the premise inventory command (independent external review, VR-005). Lean core only. -/
structure R5Bundle (n : Nat) : Prop where
  /-- first obligation -/
  pos : 0 < n
  small : n < 100

structure R5Data where
  val : Nat
  ok : val = val

theorem r5_fixture (n : Nat) {m : Nat} [Inhabited Nat] (h1 : n = m) (B : R5Bundle n) (d : R5Data)
    (hall : ∀ k, k < n → R5Bundle k) : n < 100 := B.small

theorem r5_closed : 1 + 1 = 2 := rfl
