import { Slide } from "../components/Slide";

export const SlideAnalysis = () => {
  return (
    <Slide>
      <h2 className="section-title">Analysis and Discussion</h2>
      <div className="two-col">
        <div>
          <h3 style={{ color: "var(--accent)", marginBottom: "1rem" }}>
            Transparency vs. Accuracy
          </h3>
          <p>
            Unlike deep learning models that act as black boxes, syCAMOR allows
            planners to trace exactly <em>why</em> a pixel was classified. The
            transition rules are fully inspectable.
          </p>

          <h3
            style={{
              color: "var(--accent)",
              marginTop: "1.5rem",
              marginBottom: "1rem",
            }}
          >
            Addressing Urban Heterogeneity
          </h3>
          <p>
            The fuzzy logic approach (trapezoidal memberships) handles the
            physical ambiguity of dense urban environments far better than
            binary classification.
          </p>
        </div>
        <div>
          <h3 style={{ color: "var(--accent)", marginBottom: "1rem" }}>
            The Power of Neighbourhood Context
          </h3>
          <p>
            By relying on the IDW neighbourhood evidence, syCAMOR successfully
            smoothed out SAR speckle noise without losing structural boundaries
            (like roads and building edges).
          </p>

          <h3
            style={{
              color: "var(--accent)",
              marginTop: "1.5rem",
              marginBottom: "1rem",
            }}
          >
            Epistemic Shift
          </h3>
          <p>
            Moving from "what is the model's prediction?" to "what are the first
            principles driving this classification?" This is crucial for
            high-stakes urban planning and policy evaluation.
          </p>
        </div>
      </div>
    </Slide>
  );
};
