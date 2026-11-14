/-
Independent external review (RPI-RLT-VR-005, step R5): the premise inventory command.
This text is outside Victor Rielly's Lean library. `r5-premises.sh` places it after an `import` line in a
temporary file; nothing in `formal/` imports it and it changes no declaration.

`#premise_inventory <declaration>` asks Lean for the declaration's own type and writes, as JSON:
  * every binder in order: name, binder kind, whether its type is a proposition, the head constant of its type;
  * for a binder whose type (after any leading `∀`) is a structure: that structure's fields, each marked
    proposition or data, with the field's doc comment (so a bundle of hypotheses such as `ClassifyOpenP` is opened);
  * the conclusion and its head constant;
  * the axioms the declaration depends on.
The JSON goes to the file named by the environment variable `R5_OUT`, or to the log when that is unset.
-/
open Lean Meta Elab Command in
/-- Fields of the structure at the head of `b`, or `#[]`. -/
def r5StructFields (b : Expr) : MetaM (Array Json) := do
  let .const sn _ := b.getAppFn | return #[]
  let env ← getEnv
  let some info := getStructureInfo? env sn | return #[]
  let mut out : Array Json := #[]
  for f in info.fieldNames do
    let some pn := getProjFnForField? env sn f | continue
    let pci ← getConstInfo pn
    let isP ← forallTelescope pci.type fun _ body => isProp body
    let doc ← findDocString? env pn
    out := out.push <| Json.mkObj [("field", Json.str f.toString), ("isProp", Json.bool isP),
      ("doc", match doc with | some d => Json.str d.trimAscii.toString | none => Json.null)]
  return out

open Lean Meta Elab Command in
elab "#premise_inventory " id:ident : command => do
  let n ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo id
  let ci ← getConstInfo n
  let axioms ← liftCoreM <| collectAxioms n
  let kind := match ci with
    | .thmInfo _ => "theorem" | .defnInfo _ => "definition" | .axiomInfo _ => "axiom" | _ => "other"
  let js ← liftTermElabM do
    forallTelescope ci.type fun xs body => do
      let mut arr : Array Json := #[]
      let mut i : Nat := 0
      for x in xs do
        let d ← x.fvarId!.getDecl
        let t ← instantiateMVars d.type
        let isP ← isProp t
        let bi := match d.binderInfo with
          | .default => "explicit" | .implicit => "implicit"
          | .strictImplicit => "strictImplicit" | .instImplicit => "instance"
        let (head, fields) ← forallTelescope t fun _ b => do
          let h := match b.getAppFn with | .const c _ => c.toString | _ => ""
          pure (h, ← r5StructFields b)
        let ty := (← ppExpr t).pretty 160
        arr := arr.push <| Json.mkObj [("index", toJson i), ("name", Json.str d.userName.eraseMacroScopes.toString),
          ("binder", Json.str bi), ("isProp", Json.bool isP), ("head", Json.str head),
          ("structureFields", Json.arr fields), ("type", Json.str ty)]
        i := i + 1
      let head := match body.getAppFn with | .const c _ => c.toString | _ => ""
      return Json.mkObj [("schema", Json.str "r5-premise-inventory/1"), ("declaration", Json.str n.toString),
        ("kind", Json.str kind), ("leanVersion", Json.str Lean.versionString),
        ("axioms", toJson (axioms.map (·.toString)).qsort.toList),
        ("binderCount", toJson xs.size), ("binders", Json.arr arr),
        ("conclusionHead", Json.str head), ("conclusion", Json.str ((← ppExpr body).pretty 160))]
  match ← IO.getEnv "R5_OUT" with
  | some p => IO.FS.writeFile p (js.pretty 120 ++ "\n"); logInfo m!"R5 inventory of {n} written to {p}"
  | none => logInfo m!"{js.pretty 120}"
