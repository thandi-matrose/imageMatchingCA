import { Slide } from "../components/Slide";

export const SlideRecommendations = () => {
  return (
    <Slide>
      <h2 className="section-title">Recommendations & Future Work</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
          marginTop: "2rem",
          fontSize: "21px",
        }}
      >
        <div
          style={{
            background: "white",
            padding: "1.5rem",
            borderRadius: "12px",
          }}
        >
          <h3 style={{ color: "var(--accent)", marginBottom: "1rem" }}>
            1. Algorithmic Extensions
          </h3>
          <ul style={{ paddingLeft: "1.2rem", lineHeight: "1.6" }}>
            <li style={{ marginBottom: "0.8rem" }}>
              <strong>Multi-modal Signatures:</strong> Implement multi-element
              trapezoids to split classes that have multiple local maxima (e.g.,
              Medium Density Urban).
            </li>
            <li style={{ marginBottom: "0.8rem" }}>
              <strong>VH Polarisation:</strong> Introduce the VV-VH ratio as a
              sixth feature band to better distinguish vegetation from surface
              scattering.
            </li>
            <li>
              <strong>Cumulative Distribution Functions:</strong> Test CDFs as
              an alternative to trapezoidal memberships to better model skewed
              distributions.
            </li>
          </ul>
        </div>

        <div
          style={{
            background: "white",
            padding: "1.5rem",
            borderRadius: "12px",
          }}
        >
          <h3 style={{ color: "var(--accent)", marginBottom: "1rem" }}>
            2. Practical Applications
          </h3>
          <ul style={{ paddingLeft: "1.2rem", lineHeight: "1.6" }}>
            <li style={{ marginBottom: "0.8rem" }}>
              <strong>Planner Integration:</strong> Deploy the Woodstock
              Explorer web app to local municipal planning departments for
              independent verification of land use claims.
            </li>
            <li style={{ marginBottom: "0.8rem" }}>
              <strong>Activist Toolkits:</strong> Provide open-source access to
              the benchmarking datasets and code, empowering grassroots
              movements like Reclaim the City to track displacement.
            </li>
            <li>
              <strong>Multi-temporal Analysis:</strong> Expand the pipeline to
              track the temporal evolution of gentrification over multiple years
              of Sentinel-1 acquisitions.
            </li>
          </ul>
        </div>
      </div>
    </Slide>
  );
};
