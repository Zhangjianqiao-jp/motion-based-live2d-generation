# RESEARCH_SPEC.md

# 1. Project Title

**Learning Motion Dependency from Static Illustrations for Live2D-Oriented Layer Decomposition**

**Status:** Provisional research title.  
The title intentionally emphasizes **motion dependency inference from a static image** rather than generic PSD generation, semantic segmentation, or full Live2D rig generation.

---

# 2. One-Sentence Research Question

**Can a model infer a probabilistic motion-dependency structure from a single completely unlayered RGB illustration and use that structure, together with spatial continuity, occlusion/layer-order cues, and Live2D authoring priors, to determine motion-appropriate Live2D layer boundaries?**

---

# 3. Problem Definition

## 3.1 Input

At inference time, the input is strictly:

\[
I\in\mathbb{R}^{H\times W\times 3}
\]

where \(I\) is **one static flattened RGB illustration**.

The image has:

- no PSD layers;
- no ground-truth segmentation;
- no ArtMesh;
- no Live2D rig;
- no animation sequence;
- no motion annotation;
- no control parameters;
- no physics configuration;
- no depth annotation.

The system may internally compute features, candidate regions, boundaries, semantic cues, etc. from the RGB image, but these are **predictions or preprocessing outputs**, not externally provided inference-time supervision.

---

## 3.2 Desired Output

The research target is not merely a set of semantic masks.

Conceptually, the desired latent structure is:

\[
Z=
\left(
\mathcal{L},
G_{\mathrm{motion}},
G_{\mathrm{occ}},
G_{\mathrm{author}}
\right)
\]

where:

\[
\mathcal{L}=\{L_1,\ldots,L_N\}
\]

is a proposed set of animation-appropriate layers,

\[
G_{\mathrm{motion}}
\]

describes motion dependency / relative controllability between image regions,

\[
G_{\mathrm{occ}}
\]

describes front-back / occlusion relationships,

and

\[
G_{\mathrm{author}}
\]

describes Live2D-specific structural or authoring relationships.

The **first-stage research baseline does not need to generate a full production PSD**. Its primary output may stop at a predicted motion-dependency structure and motion-induced partition.

---

## 3.3 Training-Time Information

The project assumes that training-time teacher data can come from mature, already-rigged Live2D assets.

Potentially available teacher-side information includes:

- separated original layers;
- Live2D ArtMesh geometry;
- control parameters;
- deformers;
- drawable vertex positions;
- layer order;
- parameter-driven deformation;
- physics-driven deformation;
- rendered frames under parameter interventions.

The exact dataset, file formats, licensing conditions, number of usable models, parameter conventions, and completeness of physics/rig information are **TBD**.

---

## 3.4 Inference-Time Information

Inference receives only:

\[
\boxed{I_{\mathrm{RGB}}}
\]

No teacher information is available.

In particular, inference must **not** assume access to:

\[
\theta,\quad
J,\quad
\text{PSD},\quad
\text{rig},\quad
\text{layer masks},\quad
\text{motion sequence}
\]

or any equivalent privileged representation.

---

## 3.5 What This Project Is NOT

This project is **not**:

- “given already separated Live2D layers, predict how they move”;
- “given a segmented 3D object, predict joint parameters”;
- generic semantic segmentation;
- generic anime body-part segmentation;
- generic image-to-PSD decomposition;
- generic optical-flow prediction;
- full automatic Live2D rig generation;
- commercial-scale 100–500+ layer PSD reconstruction in the first stage.

The central task is:

\[
\boxed{
\text{static unlayered RGB}
\rightarrow
\text{latent motion dependency}
\rightarrow
\text{motion-aware layer structure}
}
\]

---

# 4. Motivation

Existing segmentation and layer decomposition formulations do not directly solve the target problem because the desired layer structure is determined partly by **future animation requirements**, not only by what is visibly distinguishable in the current image.

## 4.1 Why Semantic Segmentation Is Insufficient

Semantic segmentation typically learns mappings such as:

\[
\text{pixel}\rightarrow
\{\text{hair},\text{face},\text{eye},\text{clothes},\ldots\}
\]

However, a semantic class does not uniquely determine a Live2D layer.

Examples:

- two hair strands may share the semantic label `hair` but require independent motion;
- one deformable hair strand may contain root, middle, and tip areas with very different displacement magnitudes while still belonging to one layer;
- an eye may require white, iris, highlight, and eyelid components to be separate for authoring reasons even though they form a coherent semantic structure.

Therefore:

\[
\boxed{
\text{semantic equivalence}
\neq
\text{motion-layer equivalence}
}
\]

---

## 4.2 Why Ordinary Part Segmentation Is Insufficient

Part segmentation answers:

> What visual/anatomical part does this pixel belong to?

The proposed project instead asks:

> Which regions should be independently controllable or deformable in a future Live2D rig?

These are related but not identical questions.

---

## 4.3 Why Generic Layer Decomposition Is Insufficient

Generic layered-image decomposition aims to reconstruct visually coherent RGBA components.

It does not necessarily infer:

- latent control dependencies;
- independent degrees of freedom;
- deformation coupling;
- Live2D authoring structure.

A visually correct decomposition can therefore still be inappropriate for animation.

---

## 4.4 Why Existing Live2D Decomposition Is Not the Final Research Gap

Recent methods already demonstrate that a static anime illustration can be decomposed into editable layers.

See-Through decomposes a single anime illustration into semantically distinct, fully inpainted layers and infers drawing order; its public implementation describes a pipeline producing up to 23 semantic layers and exporting PSD files.

Bunraku goes further and targets conversion of a single illustration into an editable, drivable Live2D character.

Therefore, the research question is **not**:

> Can AI generate layers?

The intended gap is narrower:

\[
\boxed{
\text{Can dynamic information contained in mature rigs teach a model
to infer motion-dependent structure from a static image?}
}
\]

---

# 5. Core Research Hypothesis

## 5.1 Current Core Hypothesis

**Status: research hypothesis; not yet experimentally validated.**

Mature Live2D models contain supervision about how different image regions respond to latent control variables.

By intervening on rig parameters and observing deformation responses, it may be possible to construct training labels representing:

- shared control support;
- motion dependency;
- independent controllability;
- deformable-component membership.

A student model can then receive only a flattened RGB rendering and learn:

\[
P(G_{\mathrm{motion}}\mid I)
\]

where \(G_{\mathrm{motion}}\) is a latent motion-dependency structure.

The intended teacher-student chain is:

\[
\boxed{
\text{mature Live2D rig}
\rightarrow
\text{parameter intervention}
\rightarrow
\text{motion response}
\rightarrow
\text{motion-dependency supervision}
}
\]

followed by:

\[
\boxed{
\text{flat RGB}
\rightarrow
\text{student}
\rightarrow
\widehat G_{\mathrm{motion}}
}
\]

and later:

\[
\boxed{
\widehat G_{\mathrm{motion}}
+
\text{spatial}
+
\text{occlusion}
+
\text{authoring}
\rightarrow
\text{layer structure}
}
\]

This chain is the current working hypothesis.

It must **not** be described as already solved.

---

# 6. Formal Mathematical Formulation

## 6.1 Static Input

Let:

\[
I\in\mathbb R^{H\times W\times 3}
\]

denote a flattened RGB illustration.

---

## 6.2 Teacher-Side Live2D Controls

For a mature rig, let:

\[
\theta=
(\theta_1,\ldots,\theta_K)
\]

denote its available control parameters.

These may correspond to head motion, gaze, blinking, hair control, deformers, physics inputs, etc.

Parameter names and semantics are not assumed to be standardized across models.

---

## 6.3 Deformation Function

Let a visible or rigged point/vertex \(v\) have image-plane position:

\[
X_v(\theta)\in\mathbb R^2.
\]

The rig therefore implicitly defines:

\[
X_v = F_v(\theta).
\]

A complete rendered image may similarly be written abstractly as:

\[
I(\theta)=R(M,\theta)
\]

for Live2D model \(M\).

---

## 6.4 Response Jacobian

A local control response may be represented as:

\[
J_{v,k}
=
\frac{\partial X_v}{\partial\theta_k}.
\]

If analytic derivatives are unavailable, the proposed teacher-side approximation is finite intervention:

\[
J_{v,k}
\approx
\frac{
X_v(\theta+\delta e_k)
-
X_v(\theta-\delta e_k)
}{
2\delta
}.
\]

This representation was discussed as a way of measuring **which controls affect which vertices**.

Exact choices of:

- perturbation size \(\delta\);
- central vs. one-sided intervention;
- parameter normalization;
- nonlinear parameter ranges;
- physics update timing

are **TBD**.

---

## 6.5 Response Signature

For a point, pixel, mesh region, or candidate region \(r\), define conceptually a response signature:

\[
C_r=
\left[
c_{r,1},
c_{r,2},
\ldots,
c_{r,K}
\right].
\]

Each \(c_{r,k}\) summarizes how region \(r\) responds to control \(\theta_k\).

The exact aggregation function is **not yet finalized**.

Possible quantities already discussed include:

- displacement response;
- response direction;
- response magnitude;
- control support;
- time-dependent response under physics.

The project must not silently freeze one definition without an experiment or explicit user decision.

---

## 6.6 Why Displacement Similarity Is Not the Correct Definition

A critical confirmed conclusion is:

\[
\boxed{
\text{similar displacement}
\neq
\text{same motion component}
}
\]

and conversely:

\[
\boxed{
\text{different displacement magnitude}
\not\Rightarrow
\text{different layer}
}
\]

Consider one deformable hair strand.

The root may have:

\[
\|\Delta X_{\mathrm{root}}\|\approx 0
\]

while the tip has:

\[
\|\Delta X_{\mathrm{tip}}\|\gg 0.
\]

They can nevertheless be driven by the same latent hair control.

A simplified shared-control model is:

\[
\Delta X(x)
=
W(x)\,\theta_{\mathrm{hair}},
\]

where \(W(x)\) changes spatially along the strand.

The relevant fact is not equal magnitude; it is that the deformation can be explained through a common latent control structure.

---

## 6.7 Shared Control Support

Conceptually define the control support of region \(r\) as:

\[
S_r=
\{k:\theta_k\text{ has a meaningful effect on }r\}.
\]

The exact threshold for “meaningful effect” is **TBD**.

Regions belonging to one deformable component may have:

\[
S_i\approx S_j
\]

even when:

\[
\|J_i\|\neq\|J_j\|.
\]

However, shared support alone is also insufficient.

For example, multiple disconnected parts can all respond to a global `AngleX` control while still requiring separate layers.

Therefore motion dependency must also consider structural relationships such as:

- attachment;
- deformation continuity;
- local spatial connectivity;
- independent secondary control;
- physics response.

---

## 6.8 Motion Dependency

The desired conceptual variable between two regions \(r_i,r_j\) is:

\[
M_{ij}
\]

representing whether they belong to a common deformable/control structure or should retain independent motion freedom.

A probabilistic form is:

\[
M_{ij}
=
P(
r_i,r_j\text{ belong to the same motion-dependent component}
).
\]

The exact mathematical teacher label for \(M_{ij}\) is currently **OPEN / TBD**.

This is a central unsolved part of the project.

---

## 6.9 Motion Affinity

A graph representation may use:

\[
A^{\mathrm{motion}}
\in[0,1]^{N\times N}
\]

where:

\[
A^{\mathrm{motion}}_{ij}
\]

measures the predicted or teacher-derived motion affinity between units \(i\) and \(j\).

High affinity should indicate that merging the regions is compatible with a shared deformable control structure.

Low affinity should indicate evidence for motion independence.

Again:

\[
A^{\mathrm{motion}}_{ij}
\]

must not be reduced to cosine similarity of displacement vectors or difference in displacement magnitude.

---

## 6.10 Student Learning Target

Two representations have been discussed.

### Option A — Direct Motion-Affinity Prediction

\[
\boxed{
I
\rightarrow
\widehat A^{\mathrm{motion}}
}
\]

The student directly predicts local or region-level motion dependency.

### Option B — Predict Response Representation First

\[
\boxed{
I
\rightarrow
\widehat J
\rightarrow
\widehat A^{\mathrm{motion}}
}
\]

The student predicts a latent response representation and derives affinity from it.

### Current Status

\[
\boxed{\text{ARCHITECTURAL CHOICE — TBD}}
\]

The project has **not** conclusively selected between these alternatives.

For the minimum viable baseline, direct affinity prediction is a reasonable provisional engineering implementation because it tests the central hypothesis with less machinery, but this must not be presented as a confirmed scientific conclusion.

---

## 6.11 Overall Probabilistic View

Since a static image does not uniquely determine how an artist would rig it, the correct conceptual mapping is:

\[
\boxed{
P(G_{\mathrm{motion}}\mid I)
}
\]

rather than assuming a deterministic physical truth:

\[
G_{\mathrm{motion}}=f(I).
\]

---

# 7. Teacher-Side Supervision Construction

## 7.1 Purpose

Teacher-side processing exists only during training/data preparation.

Its job is to transform mature Live2D assets into supervision usable by a student whose input is ultimately only RGB.

---

## 7.2 Canonical Static Rendering

For each mature Live2D model, choose a static parameter state:

\[
\theta^0.
\]

Render:

\[
I^0=R(M,\theta^0).
\]

Then flatten the rendered appearance into a normal RGB image.

The student should receive this flattened rendering, not the original separated layers.

The exact canonical-state policy is **TBD** because different Live2D assets may use different parameter ranges and rest poses.

---

## 7.3 Parameter Intervention

For each control parameter \(\theta_k\), perturb the model around the chosen state.

Conceptually:

\[
\theta_k^+
=
\theta_k^0+\delta
\]

and

\[
\theta_k^-
=
\theta_k^0-\delta.
\]

All other controllable variables should ideally remain fixed unless physics or rig dependencies make this impossible.

Then re-evaluate the rig.

---

## 7.4 Response Extraction

Record the motion response of:

- ArtMesh vertices;
- drawable geometry;
- and, if needed, rasterized visible pixels.

For each vertex:

\[
J_{v,k}
\approx
\frac{
X_v(\theta_k^+)
-
X_v(\theta_k^-)
}{
2\delta
}.
\]

This yields teacher information of the form:

\[
J
\in
\mathbb R^{N_{\mathrm{vertices}}\times K\times2}
\]

for geometric response.

This is a conceptual schema; actual tensor layout must follow the available Live2D data.

---

## 7.5 Physics

Physics is a known complication, not a solved detail.

A hair strand may respond indirectly and temporally to another parameter.

Therefore a static Jacobian may fail to capture:

- delay;
- oscillation;
- damping;
- chained response;
- parameter co-dependency.

Possible time-dependent response:

\[
J_{v,k}(t)
\]

or a sampled trajectory response may be needed.

### Status

**TBD.**

Codex must not assume that a single instantaneous finite difference fully solves physics-driven motion.

---

## 7.6 Constructing Control Signatures

Teacher-side response values should be aggregated into a representation of which controls affect which image locations or regions.

Desired properties:

- preserve shared latent-driver information;
- distinguish independent control channels;
- tolerate root-to-tip amplitude gradients;
- avoid merging unrelated regions merely because both respond to global controls.

Exact signature design is **TBD**.

---

## 7.7 Motion Dependency Ground Truth

The desired teacher output is not raw motion alone.

Teacher processing should eventually produce labels such as:

\[
G_{\mathrm{motion}}^{GT}
\]

or:

\[
A_{\mathrm{motion}}^{GT}.
\]

Potential evidence already agreed upon conceptually:

- shared control support;
- presence of independent controls;
- deformation continuity;
- spatial attachment;
- physics coupling.

However, the exact rule/function converting teacher response into binary or continuous motion affinity remains **OPEN QUESTION P0**.

---

## 7.8 Independence Boundary

An independence boundary is conceptually an image boundary across which two adjacent regions require distinct motion/control freedom.

This is not equivalent to:

- a color edge;
- a semantic boundary;
- a high optical-flow gradient;
- a difference in displacement magnitude.

Its teacher construction is **TBD** and depends on the final definition of motion dependency.

---

## 7.9 Rasterization to the Flat Image

A critical practical requirement is transferring teacher information from rig-space geometry to the flattened RGB image used by the student.

This requires a mapping such as:

\[
\text{ArtMesh vertex / layer response}
\rightarrow
\text{visible pixel / local region supervision}.
\]

Occluded pixels and hidden parts complicate this mapping.

### Status

**OPEN QUESTION.**

The baseline should initially focus on visible regions if necessary, rather than pretending hidden-region supervision is already solved.

---

# 8. Static-to-Motion Learning Problem

## 8.1 The Central Missing Mapping

The key research problem is:

\[
\boxed{
I_{\mathrm{RGB}}
\rightarrow
G_{\mathrm{motion}}
}
\]

This mapping does **not** come for free merely because teacher rigs exist.

Teacher rigs only make it possible to generate training supervision.

Whether a student can infer meaningful motion dependency from static appearance is exactly what must be experimentally tested.

---

## 8.2 Teacher-Student Setting

Training provides pairs conceptually of the form:

\[
(I^n,G_{\mathrm{motion}}^n).
\]

The student learns:

\[
f_\phi:
I
\rightarrow
P(G_{\mathrm{motion}}\mid I).
\]

At test time, only \(I\) remains.

---

## 8.3 Why This Is Not Lookup

The intended system cannot simply retrieve the exact corresponding rig because an unseen illustration may:

- have a new character design;
- combine familiar structures in novel ways;
- use different proportions;
- use different hair/clothing geometry;
- omit known semantic classes;
- admit multiple valid rigging solutions.

The goal is therefore to learn visual regularities relating static appearance to animation affordance.

---

## 8.4 Candidate Static Visual Cues

The following cues have been discussed as potentially informative:

- shape;
- local geometry;
- attachment location;
- spatial continuity;
- contour structure;
- occlusion;
- relative position;
- semantic role;
- hair-like geometry;
- clothing structure;
- material/appearance characteristics;
- thin flexible structures;
- connection to parent structures.

These cues are candidate predictive evidence.

They are **not confirmed sufficient conditions**.

---

## 8.5 Underdetermined Nature of the Problem

A single illustration does not uniquely specify a rig.

For the same visible hair strand, an author could choose:

- no secondary motion;
- one rigid layer;
- one deformable layer;
- multiple independently controlled segments;
- a physics chain.

Therefore the problem is fundamentally:

\[
\boxed{\text{one-to-many / underdetermined}}
\]

and the model should conceptually learn:

\[
P(G_{\mathrm{motion}}\mid I)
\]

rather than claim recovery of a unique ground-truth physical motion.

This ambiguity must remain explicit in both experiments and paper claims.

---

## 8.6 Core Question to Validate

The first research question is:

> **Does static visual information contain enough learnable statistical signal to predict motion-dependency structure that generalizes to unseen characters?**

This is not currently known.

---

# 9. Layer Construction

## 9.1 Four Factors

The final layer decision is currently understood to depend on four interacting factors.

### Factor 1 — Spatial / Shape Continuity

Nearby, visually continuous pixels normally have a prior toward belonging to the same component.

This is a soft prior, not a hard rule.

Disconnected visible fragments may still belong to one semantic or hidden component under occlusion.

---

### Factor 2 — Occlusion / Layer Order

The flat illustration contains cues about:

\[
L_i \succ L_j
\]

meaning layer \(L_i\) lies in front of layer \(L_j\).

This determines stacking/depth relationships rather than motion independence itself.

---

### Factor 3 — Motion Dependency

Regions that require genuinely independent controllability should be separable.

Regions with different local deformation magnitude may still remain one layer if they share a coherent latent control structure.

---

### Factor 4 — Live2D Authoring Prior

Some splitting decisions arise from production requirements rather than purely geometric or physical motion.

Examples include functionally distinct eye components or other structures that need separate editability/control.

This prior must remain distinct from pure motion.

Its exact formalization is **TBD**.

---

## 9.2 These Factors Are Coupled

A previously considered simple expression such as:

\[
E
=
\lambda_s E_s+
\lambda_d E_d+
\lambda_m E_m+
\lambda_a E_a
\]

may be useful as a conceptual sketch but is **not a confirmed optimization formulation**.

The factors can be dependent.

For example:

- an occlusion cue can affect whether a color boundary indicates another layer;
- authoring semantics can override pure spatial continuity;
- motion independence must be interpreted together with attachment and continuity.

Therefore the current conceptual formulation is joint structured inference, e.g.:

\[
P(
\mathcal L,
G_{\mathrm{occ}},
G_{\mathrm{motion}},
G_{\mathrm{author}}
\mid I
).
\]

The exact solver is **TBD**.

---

## 9.3 Possible Layer-Constructions Already Discussed

The conversation has mentioned:

- graph partition;
- graph clustering;
- structured decoder;
- hierarchical/recursive splitting.

No final choice has been made.

Codex must not treat any one of these as finalized unless explicitly selected during implementation.

---

## 9.4 Outline / Shadow / Highlight

The project has also identified outline, shadow, and highlight as appearance components that can interfere with structural segmentation.

Current interpretation:

\[
\boxed{
\text{outline/shadow/highlight handling is auxiliary appearance decomposition,
not a fifth motion constraint}
}
\]

The intended purpose is to avoid treating illumination/style changes as genuine structural boundaries.

Potential outputs may include:

- base/color component;
- outline;
- shadow;
- highlight.

However:

- the exact decomposition method is not selected;
- it is not currently the central research contribution;
- it must not expand the first baseline into a full production-layer reconstruction problem.

For the first experiment, this module can remain optional unless appearance boundaries prevent meaningful evaluation of motion dependency.

---

# 10. Relationship to Existing Work

## 10.1 Learning to Predict Part Mobility from a Single Static Snapshot

**Hu et al., 2017, “Learning to Predict Part Mobility from a Single Static Snapshot.”**

### What it solves

The method assumes a 3D object has already been segmented into moving/reference part pairs and predicts the mobility of these known parts from a static 3D snapshot. Training units contain several motion states and associated motion parameters.

### What it provides

Useful conceptual ideas:

- static-to-dynamic mapping;
- relative part mobility;
- motion prior learned from examples;
- separation of motion prediction and motion realization.

### What it does not solve

It assumes the moving/reference parts are already segmented.

The paper explicitly notes that its input shapes are segmented and that a fully automatic system depends on segmentation quality.

### Relationship to this project

Our problem moves the inference point earlier:

\[
\text{flat RGB}
\rightarrow
\text{discover motion-relevant structure}
\]

instead of:

\[
\text{known 3D parts}
\rightarrow
\text{predict their mobility}.
\]

---

## 10.2 See-Through

**“See-through: Single-image Layer Decomposition for Anime Characters.”**

### What it solves

See-Through performs single-image anime-character layer decomposition, including semantic layer separation, hidden-region completion, and drawing-order inference.

### What it provides

Potentially reusable or comparable components include:

- anime layer decomposition;
- semantic body-part structure;
- pseudo-depth / drawing-order logic;
- transparent-layer reconstruction;
- existing training/data pipeline.

### What it does not solve

Its primary decomposition objective is semantic/layer reconstruction rather than explicit inference of a latent **motion-dependency graph from static RGB**.

### Relationship to this project

See-Through is an important baseline and potential engineering component, but **semantic layer decomposition is not our research endpoint**.

---

## 10.3 Bunraku

**“Bunraku: Turning a Single Illustration into an Editable Live2D Character.”**

### What it solves

Bunraku targets the end-to-end conversion of one illustration into an editable, drivable Live2D character.

### What it provides

It demonstrates that the broader objective of generating editable Live2D assets from a single image is already being actively addressed.

It is therefore relevant for:

- task positioning;
- comparison;
- Live2D layer/rig representation;
- evaluation of end-to-end capabilities.

### What it does not establish for this project

The existence of an end-to-end Live2D generation system does not by itself answer:

\[
\text{Can rig-derived motion dependency supervision be learned from static RGB?}
\]

### Relationship to this project

Our intended scientific gap is narrower:

\[
\boxed{
\text{motion-conditioned / motion-dependency-aware layer inference}
}
\]

rather than the generic question of whether a model can output Live2D-compatible layers.

---

## 10.4 OmniPSD

**“OmniPSD: Layered PSD Generation with Diffusion Transformer.”**

### What it solves

OmniPSD supports text-to-PSD generation and image-to-PSD decomposition, extracting editable RGBA layers from flattened images.

### What it provides

It is relevant as a generic modern PSD/layer-decomposition reference or baseline.

### What it does not solve

It is not specifically designed to infer Live2D motion dependency or independent deformability from static anime imagery.

### Relationship to this project

It can test whether general-purpose PSD decomposition already recovers useful animation structure without motion-derived supervision.

---

## 10.5 Motion-Supervised Part Discovery

The conversation also identified motion-supervised part/co-part segmentation as conceptually relevant because those works use observed motion to discover meaningful parts.

### Relationship

Our proposed supervision differs because training motion can come from controlled interventions on a rig rather than ordinary video motion.

The unresolved part is the same central issue:

\[
\text{How does dynamic training supervision create a predictor that works from static RGB alone?}
\]

No specific external method is adopted as the final solution.

---

# 11. Minimum Viable Research Baseline

The MVP must answer one question:

\[
\boxed{
\text{Can static RGB predict meaningful motion-dependency structure?}
}
\]

It must **not** attempt to complete the commercial Live2D production pipeline.

---

## 11.1 Dataset / Supervision Source

Use a subset of mature rigged Live2D assets for which it is possible to:

1. render a flattened RGB image;
2. intervene on control parameters;
3. observe vertex/drawable responses.

Exact corpus and size: **TBD**.

Train/validation/test splitting must be performed at the **character/model level**, not by rendering frames from the same character into different splits.

This prevents identity leakage.

---

## 11.2 Teacher Signal

Minimum teacher pipeline:

\[
\text{rig}
\rightarrow
\text{control interventions}
\rightarrow
\text{response representation}
\rightarrow
\text{motion-dependency labels}.
\]

The exact dependency-label formula is a required early experiment.

At minimum, labels must encode more than motion magnitude.

---

## 11.3 Student Input

Strictly:

\[
\boxed{\text{flattened static RGB}}
\]

No rig-derived channels.

No GT segmentation.

No PSD metadata.

---

## 11.4 Student Target

### Provisional MVP Engineering Choice

Predict local or region-level:

\[
\widehat A^{\mathrm{motion}}
\]

from RGB.

This is a provisional baseline because it directly evaluates static-to-motion learning.

It is **not** yet a final architectural commitment.

---

## 11.5 Prediction Units

The final project may use pixels, local patches, candidate regions, or learned regions.

### MVP Requirement

Whatever representation is chosen:

- it must be computable from RGB alone;
- GT layer masks cannot be supplied at inference;
- any candidate segmentation must be an internal image-derived module.

Exact representation: **TBD**.

---

## 11.6 Minimal Model

Keep the first student simple:

\[
I
\xrightarrow{\text{image encoder}}
F
\xrightarrow{\text{relation predictor}}
\widehat A^{\mathrm{motion}}.
\]

Do not begin with a large diffusion system or full end-to-end Live2D generator.

The purpose is hypothesis testing, not maximum visual quality.

Exact backbone: **TBD**.

---

## 11.7 Minimal Layer Construction

After obtaining predicted affinity, apply a simple graph-based partition or clustering procedure to produce a visualization of motion-induced components.

This partition is only an interpretation of the predicted motion graph.

It is not yet the final four-factor Live2D layer solver.

Exact graph algorithm: **TBD**.

---

## 11.8 Evaluation

At minimum evaluate on held-out characters:

1. motion-dependency edge prediction;
2. motion-independence boundary prediction;
3. whether predicted affinity creates coherent motion-induced components.

Evaluation must compare against teacher-derived motion labels.

---

## 11.9 Required Visualizations

For each evaluation example save:

- input flattened RGB;
- teacher motion-response visualization;
- teacher motion-affinity / dependency visualization;
- predicted motion affinity;
- GT independence boundaries;
- predicted independence boundaries;
- resulting motion-induced partition;
- failure-case annotations.

A required qualitative case is the discussed:

> hair root vs. hair tip

to ensure the model is not simply using motion magnitude as the definition of layer membership.

---

# 12. Baselines to Compare Against

Keep comparisons limited to hypotheses actually relevant to the paper.

## 12.1 Semantic / Part-Based Baseline

A static-image semantic or part decomposition system.

Purpose:

> Test whether ordinary semantic structure already explains the teacher motion-dependency labels.

---

## 12.2 Appearance / Spatial-Only Baseline

Predict grouping using static visual continuity and boundaries without motion-derived supervision.

Purpose:

> Test whether generic appearance boundaries explain motion-induced boundaries.

---

## 12.3 Motion-Supervised Student

Same inference condition:

\[
\text{RGB only}
\]

but trained using teacher-derived motion dependency.

This is the proposed method/baseline target.

Purpose:

> Test whether dynamic teacher supervision improves prediction of motion-relevant structure.

---

## 12.4 Existing Layer-Decomposition Baseline

Where practical, compare resulting layers/partitions with:

- See-Through;
- OmniPSD;
- Bunraku if compatible outputs and code/data access permit.

These comparisons should not be forced if output spaces cannot be meaningfully aligned.

---

# 13. Evaluation

Evaluation must be divided by hypothesis.

## 13.1 Motion Dependency Prediction

Evaluate whether the student predicts teacher-defined motion relations.

Possible standard quantities:

- precision;
- recall;
- F1;
- average precision / PR behavior;
- ROC-AUC where meaningful.

Exact primary metric: **TBD after label distribution is inspected**.

### Hypothesis Tested

\[
\boxed{
\text{Static RGB contains learnable information about motion dependency.}
}
\]

---

## 13.2 Motion-Independence Boundary Quality

Compare predicted boundaries against teacher-derived independence boundaries.

Use boundary precision/recall/F1 or an equivalent standard boundary measure.

### Hypothesis Tested

Whether the model can spatially localize where independent deformable components should separate.

---

## 13.3 Motion-Induced Component / Layer Quality

Once teacher motion components have a finalized definition, compare predicted partitions with them.

Exact partition metric is **TBD**.

Do not claim layer quality before the ground-truth notion of motion component is stable.

---

## 13.4 Final Layer Quality

Later-stage evaluation should assess the combined:

- spatial;
- occlusion;
- motion;
- authoring

layer structure.

This is outside the first milestone.

---

## 13.5 Downstream Animation / Editability

Potential later evaluation may ask:

- can predicted layers be independently manipulated?
- do they avoid visually incorrect coupling?
- are expected deformable structures preserved?

Exact evaluation protocol is **TBD**.

This must not be replaced with only:

- PSNR;
- SSIM;
- reconstruction similarity.

Pixel reconstruction alone does not validate motion-aware decomposition.

---

# 14. Required Ablations

Only run ablations that answer core research questions.

## 14.1 Without Motion-Derived Supervision

Remove/replace motion-derived labels.

Purpose:

> Determine whether motion supervision contributes information beyond ordinary static decomposition.

---

## 14.2 Motion Magnitude vs. Shared-Control Representation

Compare a naive target based on displacement similarity/magnitude with a representation using shared control support / response structure.

Purpose:

> Directly test the hair-root/hair-tip objection.

Expected question:

\[
\text{Does shared-control modeling prevent over-segmentation of deformable parts?}
\]

No expected result may be assumed before experimentation.

---

## 14.3 Without Spatial Prior

Purpose:

> Test whether motion prediction alone produces fragmented or disconnected components.

Relevant mainly after motion prediction itself works.

---

## 14.4 Without Occlusion Prior

Purpose:

> Test whether layer-order information contributes to final structural decomposition.

Not required for the very first static-to-motion milestone.

---

## 14.5 Without Authoring Prior

Purpose:

> Distinguish motion-physical grouping from Live2D production-driven layer splitting.

Not required for the first static-to-motion milestone.

---

## 14.6 Alternative Motion Representation

Potential comparison:

\[
I\rightarrow\widehat A_{\mathrm{motion}}
\]

versus:

\[
I\rightarrow\widehat J\rightarrow\widehat A_{\mathrm{motion}}.
\]

### Status

Do not implement this ablation until there is a clear reason to test both.

It remains an architectural **TBD**, not a required first experiment.

---

# 15. Current Confirmed Decisions

## Research Target

- [x] Inference input is a **single completely flattened static RGB illustration**.
- [x] Inference does **not** receive PSD layers.
- [x] Inference does **not** receive rig information.
- [x] Inference does **not** receive motion annotation.
- [x] Inference does **not** receive GT segmentation.
- [x] Semantic segmentation is not the final research target.
- [x] Generic PSD generation is not the central innovation.
- [x] The central latent target is motion dependency / motion independence relevant to future layer construction.
- [x] Existing rigged Live2D assets are training-side teachers, not inference-time inputs.

## Motion Definition

- [x] Motion magnitude similarity is insufficient.
- [x] Different movement magnitudes can belong to one deformable component.
- [x] Hair root and tip are the canonical counterexample.
- [x] Shared latent control / response signature is a core concept.
- [x] Motion dependency is relational, not merely a per-pixel displacement label.
- [x] Static-image motion inference is underdetermined and should conceptually be probabilistic.

## Layering

- [x] Final layer reasoning contains at least four factors:
  - spatial/shape continuity;
  - occlusion/layer order;
  - motion dependency;
  - Live2D authoring prior.
- [x] These four factors are not assumed independent.
- [x] A simple fixed linear weighted sum is not a confirmed final formulation.
- [x] Outline/shadow/highlight are relevant auxiliary appearance components but are not a fifth motion factor.

## Engineering / Architecture

- [ ] Exact pixel/region representation selected.
- [ ] Exact teacher response-signature definition selected.
- [ ] Exact teacher motion-affinity definition selected.
- [ ] Exact handling of physics finalized.
- [ ] Direct affinity vs. response-field student target selected.
- [ ] Static student architecture selected.
- [ ] Graph partition / clustering / structured-decoder method selected.
- [ ] Occlusion model selected.
- [ ] Authoring prior representation selected.
- [ ] Outline/shadow/highlight module selected.
- [ ] Existing repository to fork selected.
- [ ] Exact dataset and sample count confirmed.
- [ ] Primary quantitative metrics finalized.
- [ ] Full PSD reconstruction included in scope.

---

# 16. Rejected / Deprecated Ideas

## Idea: Treat the Final Task as “Given Separated Live2D Parts, Predict Their Motion”

**Why considered:**  
The 3D part-mobility paper provides a clear formulation for predicting motion of known parts.

**Why rejected:**  
It begins after segmentation has already been solved. Our inference input has no parts or layers.

**Do not reintroduce unless:**  
Used only as a conceptual or teacher-side reference, not as the final task formulation.

---

## Idea: Use Motion Magnitude Similarity as Layer Affinity

**Why considered:**  
Simple to compute from rendered motion.

**Why rejected:**  
A deformable component can have strongly varying local displacement. Hair roots and tips are the canonical counterexample.

**Do not reintroduce unless:**  
Only as a deliberately weak ablation/baseline.

---

## Idea: “If Two Regions Move Differently, They Must Be Different Layers”

**Why considered:**  
It gives a simple motion segmentation rule.

**Why rejected:**  
Deformation within one layer naturally creates spatially varying motion.

**Do not reintroduce unless:**  
Never as the main definition; only as a naive baseline.

---

## Idea: “If Two Regions Respond to the Same Control, They Must Be the Same Layer”

**Why considered:**  
Shared control support is more meaningful than equal displacement.

**Why rejected:**  
Global controls such as head rotation can affect many distinct layers simultaneously.

**Do not reintroduce unless:**  
Combined with structural, local, and independence evidence.

---

## Idea: Pure Semantic Segmentation as the Main Research Objective

**Why considered:**  
Anime body-part segmentation is easier and existing methods are mature.

**Why rejected:**  
Semantic identity does not determine independent future controllability.

**Do not reintroduce unless:**  
Used as one input cue or baseline.

---

## Idea: Generic Image-to-PSD as the Main Contribution

**Why considered:**  
The long-term project ultimately needs layered assets.

**Why rejected:**  
Existing work already addresses substantial portions of image decomposition / editable-layer generation.

**Do not reintroduce unless:**  
Used as an engineering module, comparison, or downstream extension.

---

## Idea: Four Completely Independent Loss Terms Combined by Fixed Linear Weights

**Why considered:**  
It provides a convenient mathematical formulation.

**Why rejected:**  
Spatial, depth, motion, and authoring evidence interact and may conflict.

**Do not reintroduce unless:**  
Used explicitly as a simple baseline against a joint model.

---

## Idea: Start by Building a Full Commercial Live2D Production System

**Why considered:**  
The long-term goal involves commercial-quality layer structures.

**Why rejected:**  
It would mix many engineering problems before validating the central scientific hypothesis.

**Do not reintroduce unless:**  
The static-RGB-to-motion-dependency hypothesis is first experimentally validated.

---

# 17. Open Research Questions

# P0 — Blocking / Core Scientific Questions

## P0.1 Exact Definition of Motion Dependency

How should rig responses be converted into:

\[
A_{\mathrm{motion}}^{GT}?
\]

The definition must distinguish:

- one deformable component with spatially varying response;
- two independently controllable components;
- two different components sharing a global driver.

This is currently the most important unresolved teacher-label problem.

---

## P0.2 Static RGB → Motion Dependency Generalization

Can a student actually learn:

\[
P(G_{\mathrm{motion}}\mid I)
\]

for unseen characters?

What static information is sufficient?

This is the project's central experimental question and is **not already solved by generating teacher labels**.

---

## P0.3 Student Target Representation

Should the student learn:

\[
I\rightarrow\widehat A_{\mathrm{motion}}
\]

directly,

or:

\[
I\rightarrow\widehat J
\rightarrow\widehat A_{\mathrm{motion}}?
\]

No final decision has been made.

---

## P0.4 Physics and Coupled Motion

How should teacher supervision represent:

- delayed physics response;
- oscillation;
- chained deformers;
- multiple parameters affecting one component;
- dependent control parameters?

Instantaneous independent parameter perturbation may be insufficient.

---

## P0.5 Rig-Space → RGB-Space Label Transfer

How should mesh/control response be converted into supervision for the flattened visible image, particularly at:

- overlaps;
- occlusion boundaries;
- transparent pixels;
- hidden regions?

---

# P1 — Important Structural Questions

## P1.1 Prediction Unit

Should motion relations operate over:

- pixels;
- local patches;
- superpixels;
- candidate regions;
- learned regions?

Must not require GT segmentation at test time.

---

## P1.2 Four-Factor Fusion

How should:

\[
G_{\mathrm{motion}},
G_{\mathrm{spatial}},
G_{\mathrm{occ}},
G_{\mathrm{author}}
\]

interact?

Graph clustering, structured decoding, factorized prediction, and recursive splitting have been discussed but not selected.

---

## P1.3 Live2D Authoring Prior

What exactly constitutes an authoring prior independent from motion?

How is it extracted consistently from existing mature Live2D models?

---

## P1.4 Global Controls vs. Local Motion Components

How should the system avoid merging all regions responding to a shared global control such as head rotation?

A valid motion-dependency measure needs to distinguish:

\[
\text{co-motion due to parent transform}
\]

from:

\[
\text{membership in one deformable component}.
\]

---

## P1.5 Outline / Shadow / Highlight Interaction

Should these components be removed before motion-layer prediction, predicted jointly, or attached after base-layer inference?

This remains a supporting subproblem.

---

# P2 — Later-Stage Questions

## P2.1 Hidden-Region Completion

How to reconstruct invisible RGBA content after layer structure is known.

Not required for first baseline.

---

## P2.2 Full Layer Ordering

How to robustly infer a global DAG of drawing order.

Not required for first static-to-motion milestone.

---

## P2.3 Complete Rig Generation

How to create ArtMesh, deformer structure, parameters, and physics automatically.

Outside the first research scope.

---

## P2.4 Commercial-Scale Granularity

How to scale to very large professional PSD/Live2D projects.

Outside the first baseline.

---

# 18. Implementation Boundary

The first implementation must **not** attempt to solve all Live2D authoring.

Do not initially implement:

- complete commercial PSD generation;
- hundreds of production layers;
- complete Live2D rig generation;
- automatic ArtMesh generation;
- full physics authoring;
- hidden-region diffusion reconstruction;
- perfect line/shadow/highlight reconstruction;
- GUI/editor;
- web application;
- agent framework;
- complicated workflow orchestration;
- performance optimization before correctness;
- large-scale distributed training before a small experiment runs;
- end-to-end diffusion generation unless later experiments justify it.

The first implementation should focus on:

\[
\boxed{
\text{rig-derived teacher labels}
+
\text{RGB-only student}
+
\text{motion-dependency evaluation}
}
\]

Everything else is secondary.

---

# 19. Recommended Repository Structure

```text
project_root/
├── RESEARCH_SPEC.md
├── README.md
│
├── configs/
│   ├── teacher/
│   ├── student/
│   └── experiments/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── renders/
│   └── splits/
│
├── src/
│   ├── data/
│   │   ├── dataset.py
│   │   └── transforms.py
│   │
│   ├── teacher/
│   │   ├── live2d_loader.*
│   │   ├── parameter_intervention.*
│   │   ├── response_extraction.*
│   │   ├── response_signature.*
│   │   └── motion_affinity.*
│   │
│   ├── models/
│   │   ├── encoder.py
│   │   └── motion_relation_head.py
│   │
│   ├── layering/
│   │   └── graph_partition.py
│   │
│   └── evaluation/
│       ├── motion_metrics.py
│       ├── boundary_metrics.py
│       └── visualization.py
│
├── scripts/
│   ├── inspect_live2d_data.*
│   ├── render_static_images.*
│   ├── extract_teacher_responses.*
│   ├── build_motion_labels.*
│   ├── train_student.py
│   └── evaluate_student.py
│
├── experiments/
│   └── README.md
│
├── tests/
│   ├── test_teacher_response.*
│   ├── test_data_alignment.*
│   └── test_metrics.*
│
└── docs/
    ├── data_format.md
    ├── teacher_label_definition.md
    └── experiment_log.md
```

Notes:

- File extensions for Live2D-specific extraction code depend on the actual SDK/runtime and are deliberately not fixed here.
- Do not create unnecessary abstraction layers before inspecting the real dataset.
- `teacher_label_definition.md` should record every change to the definition of motion affinity so experiments remain reproducible.

---

# 20. First Experimental Milestone

## Milestone M1

The baseline first stage is considered established only when the following complete pipeline runs on held-out characters:

\[
\boxed{
\text{mature rig}
\rightarrow
\text{teacher response}
\rightarrow
\text{motion-dependency label}
}
\]

for training data,

and:

\[
\boxed{
\text{static RGB only}
\rightarrow
\text{student}
\rightarrow
\widehat G_{\mathrm{motion}}
}
\]

for validation/test data.

M1 must produce measurable results and visualizations.

### Required Outputs

For multiple held-out Live2D characters:

1. flattened RGB input;
2. teacher control-response visualization;
3. teacher motion-affinity/dependency target;
4. student-predicted motion affinity;
5. teacher independence boundaries;
6. predicted independence boundaries;
7. simple graph partition derived from prediction;
8. quantitative motion-dependency metrics;
9. qualitative failure cases.

### Required Core Comparison

At minimum compare:

\[
\text{appearance/spatial-only}
\]

against:

\[
\text{motion-supervised RGB student}.
\]

### M1 Scientific Success Criterion

Do **not** define success as a predetermined numeric score before observing the dataset.

M1 is scientifically successful if the experiment can answer, with held-out-character evidence:

> Does motion-derived teacher supervision provide predictive signal from static RGB beyond ordinary appearance/semantic grouping?

A null result is still a valid research result and must be recorded.

### Required Sanity Case

The visualizations must include deformable structures where motion magnitude changes spatially, especially hair root-to-tip behavior.

If the teacher labels themselves split a single continuously controlled hair strand solely because its tip moves more than its root, the teacher-label definition is invalid and M1 must stop until that definition is corrected.

---

# 21. Codex Handoff Summary

You are taking over a research project whose central task is **not generic Live2D generation and not semantic segmentation**.

The inference problem is fixed:

\[
\boxed{
\text{one unlayered static RGB illustration}
\rightarrow
\text{predicted latent motion dependency}
}
\]

followed eventually by motion-aware layer construction.

Training may exploit mature Live2D rigs as privileged teachers.

The critical intended learning bridge is:

\[
\text{rig}
\rightarrow
\text{interventions}
\rightarrow
\text{response supervision}
\]

during data generation,

then:

\[
\boxed{
\text{RGB only}
\rightarrow
\widehat G_{\mathrm{motion}}
}
\]

during student inference.

### Do Not Change These Points Without User Approval

1. Do not provide PSD/layer/rig/motion information to the student at inference.
2. Do not redefine the problem as semantic segmentation.
3. Do not redefine motion dependency as displacement similarity.
4. Do not assume different motion amplitude implies different layers.
5. Do not assume shared global control implies same layer.
6. Do not replace the four-factor final formulation with motion-only segmentation.
7. Do not begin with a full commercial Live2D generation pipeline.
8. Do not silently introduce a new paper, model family, dataset, optimization method, or task definition as a core design decision.
9. Do not report unverified results or invented dataset statistics.
10. Do not treat the existence of teacher rig supervision as proof that static RGB → motion dependency is solved.

### First Implementation Priority

Before training a sophisticated network:

1. inspect the real Live2D training assets;
2. determine which control/mesh/physics information is actually accessible;
3. implement deterministic parameter intervention and response extraction;
4. visualize response signatures;
5. establish a defensible teacher motion-dependency target;
6. only then train a small RGB-only student.

### Stop and Ask the User If

- the available Live2D dataset lacks the assumed rig/control information;
- the data format cannot expose vertex/deformation response;
- a choice must be made between incompatible definitions of motion dependency;
- physics behavior makes independent parameter intervention invalid;
- a proposed implementation would require GT segmentation at inference;
- an existing repository would materially change the research formulation;
- the only way forward appears to require changing the central task;
- the teacher labels systematically contradict the shared-control/deformable-component definition;
- a new major assumption is required that is not contained in this specification.

The first stage exists to test one claim:

\[
\boxed{
\text{Can motion structure learned from rigged Live2D assets
be predicted from static RGB on unseen characters?}
\]

Do not expand the project until that question has a reproducible experimental answer.

---

# 22. SELF-CHECK

## A. Did this specification mistake “dynamic rig data can generate supervision” for solving “static RGB → motion dependency”?

**No.**

The distinction is explicit.

Teacher supervision construction is training-side only, while the static-to-motion mapping remains a central P0 research question.

---

## B. Does inference silently assume segmentation / PSD / rig / motion?

**No.**

Inference explicitly receives only:

\[
I_{\mathrm{RGB}}.
\]

Any segmentation or region proposal used internally must itself be derived from RGB and cannot be ground truth.

---

## C. Is semantic segmentation treated as the final target?

**No.**

It is only a possible cue/baseline.

The research target is motion-dependency-aware layer structure.

---

## D. Is motion similarity confused with motion dependency?

**No.**

The specification explicitly rejects:

\[
\text{equal motion magnitude}
\Leftrightarrow
\text{same layer}.
\]

Shared latent controls, deformation continuity, independent controllability, and structural attachment are preserved as the intended concepts.

---

## E. Is the older commercial PSD objective mixed with the current research baseline?

**No.**

Full commercial PSD reconstruction, hidden completion, complete rigging, and large layer counts are explicitly outside M1.

---

## F. Are unresolved questions presented as solved?

**No.**

The following remain explicitly TBD / OPEN:

- teacher motion-dependency definition;
- physics handling;
- RGB-to-motion architecture;
- direct affinity vs. response prediction;
- pixel vs. region representation;
- four-factor fusion;
- authoring prior formalization;
- auxiliary appearance decomposition;
- exact evaluation metrics;
- full layer-construction algorithm.

---

## G. Is the baseline small enough to execute?

**Yes.**

The minimum experimental loop is deliberately limited to:

\[
\boxed{
\text{rig teacher}
\rightarrow
\text{motion labels}
\rightarrow
\text{RGB-only student}
\rightarrow
\text{motion-dependency evaluation}
}
\]

before implementing a full Live2D production pipeline.
