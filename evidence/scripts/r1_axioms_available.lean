/-
Independent external review (RPI-RLT-VR-004, step R1). This file is outside Victor Rielly's Lean library: nothing in
`formal/` imports it, and it changes no declaration. It asks Lean two questions about named theorems of
`formal/ZK60Formal` at commit eee3eb57:

1. `#print axioms`: which axioms does the theorem's proof depend on?
2. `#premises`: how many binders does the theorem's statement take, and how many of them are propositional
   hypotheses (premises that a concrete instance would have to discharge)?

This is the PARTIAL form of `r1_axioms_premises.lean`: it imports only modules that built on the reviewer's
6 GiB machine, so it leaves out every run-level `…productionReady…` theorem (their modules sit downstream of
`ZK60Formal.RunExtractClassify`, which needs more memory to compile). Run from `formal/`:
    lake env lean ../evidence/scripts/r1_axioms_available.lean
-/
import ZK60Formal.Statements
import ZK60Formal.StatementsD76Leaky
import ZK60Formal.StatementsD76Bridge
import ZK60Formal.RunShapeShield
import ZK60Formal.Assembly
import ZK60Formal.AssembleClassify
import ZK60Formal.BindingEP
import ZK60Formal.SoundMProduct
import ZK60Formal.SoundOpeningRO
import ZK60Formal.FSCompose
import ZK60Formal.FSOpening
import ZK60Formal.FSLogUp
import ZK60Formal.HidingBlock
import ZK60Formal.HidingMOpening
import ZK60Formal.HidingMerkle
import ZK60Formal.SoundMerkle
import ZK60Formal.BlockLookDone
import ZK60Formal.BlockR13StmtDone

open Lean Meta Elab Command

/-- Print the binder count of a theorem's statement, split into data binders and propositional hypotheses. -/
elab "#premises " id:ident : command => do
  let n ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo id
  let ci ← getConstInfo n
  liftTermElabM do
    forallTelescope ci.type fun xs body => do
      let mut props : Array Name := #[]
      let mut data : Nat := 0
      let mut inst : Nat := 0
      for x in xs do
        let t ← inferType x
        let d ← x.fvarId!.getDecl
        if ← isProp t then
          props := props.push d.userName
        else if d.binderInfo.isInstImplicit then
          inst := inst + 1
        else
          data := data + 1
      logInfo m!"PREMISES {n}: {xs.size} binders = {data} data + {inst} instance + {props.size} propositional hypotheses\nconclusion head: {body.getAppFn}\nhypotheses: {props.toList}"

-- The approved gate and its statements (definitions; listed so the log names what the conclusions mean).
#check @ZK60.ProductionReadyL
#check @ZK60.KnowledgeSound
#check @ZK60.ZeroKnowledgeL

-- Block level: the app's block at all 26 Shieldstral layers, and the development rungs.
#premises ZK60.Exec.Block.Join.R13H.block_knowledge_r13_shield
#print axioms ZK60.Exec.Block.Join.R13H.block_knowledge_r13_shield
#premises ZK60.Exec.Block.Join.R13H.block_knowledge_r13_rung
#print axioms ZK60.Exec.Block.Join.R13H.block_knowledge_r13_rung

-- Statements, model and gate sanity.
#print axioms ZK60.D76.leaky_not_productionReadyL
#print axioms ZK60.RunShape.Shield.shield_circuitIff
#print axioms ZK60.Assembly.semanticHiding_of_zeroKnowledge
#print axioms ZK60.trivialArith_circuitIff

-- Components: the F12 pair, the opening with extraction, Fiat-Shamir, hiding.
#print axioms ZK60.Sound.mproduct_sound_shift
#print axioms ZK60.Sound.mproduct_offset_accepts
#print axioms ZK60.Sound.opening_sound_extracted
#print axioms ZK60.Sound.MerkleEnc.merkle_binding
#print axioms ZK60.Sound.sumcheck_sound
#print axioms ZK60.Sound.logup_block_bound
#print axioms ZK60.Sound.rs_proximity_half
