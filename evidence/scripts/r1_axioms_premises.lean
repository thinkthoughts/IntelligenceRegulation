/-
Independent external review (RPI-RLT-VR-004, step R1). This file is outside Victor Rielly's Lean library: nothing in
`formal/` imports it, and it changes no declaration. It asks Lean two questions about named theorems of
`formal/ZK60Formal` at commit eee3eb57:

1. `#print axioms`: which axioms does the theorem's proof depend on?
2. `#premises`: how many binders does the theorem's statement take, and how many of them are propositional
   hypotheses (premises that a concrete instance would have to discharge)?

Run from `formal/`, after `lake build`:
    lake env lean ../evidence/scripts/r1_axioms_premises.lean
-/
import ZK60Formal

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

-- Run-level top theorems for the classifier app, oldest to newest.
#premises ZK60.ProtocolClassify.rt_productionReady_r13
#print axioms ZK60.ProtocolClassify.rt_productionReady_r13
#premises ZK60.ProtocolClassify.RunShapeP.cb_productionReadyL_epP_codeF
#print axioms ZK60.ProtocolClassify.RunShapeP.cb_productionReadyL_epP_codeF
#premises ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_view
#print axioms ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_view
#premises ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_real
#print axioms ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_real

-- Block level and components.
#premises ZK60.Exec.Block.Join.R13H.block_knowledge_r13_shield
#print axioms ZK60.Exec.Block.Join.R13H.block_knowledge_r13_shield
#print axioms ZK60.D76.leaky_not_productionReadyL
#print axioms ZK60.RunShape.Shield.shield_circuitIff
#print axioms ZK60.Assembly.semanticHiding_of_zeroKnowledge
#print axioms ZK60.Sound.mproduct_sound_shift
#print axioms ZK60.Sound.mproduct_offset_accepts
#print axioms ZK60.trivialArith_circuitIff
