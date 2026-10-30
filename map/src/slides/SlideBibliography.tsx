import { Slide } from "../components/Slide";
import { motion } from "framer-motion";

export const SlideBibliography = () => {
  const references = [
    {
      text: "Campbell, E., & Donaldson, R. (2025). All in the mix: Neighbourhood aesthetics, artwashing, and gentrification in Salt River, Cape Town. ",
      journal: "Journal of Housing and the Built Environment",
      details: ", 40(3), 1061–1087.",
    },
    {
      text: "Daniel, A. (2024). Multi-layered encounters between reclaim the city and the cape town municipality. ",
      journal:
        "Canadian Journal of African Studies/Revue canadienne des études africaines",
      details: ", 58(2), 263–280.",
    },
    {
      text: "Pluto-Kossakowska, J., & Wangiyana, S. (2025). Supervised semantic segmentation of urban area using SAR. ",
      journal: "Remote Sensing",
      details: ", 17(9). ",
      url: "https://doi.org/10.3390/rs17091606",
    },
    {
      text: "Sanchez, T. W., Brenman, M., & Ye, X. (2025). The ethical concerns of artificial intelligence in urban planning. ",
      journal: "Journal of the American Planning Association",
      details: ", 91(2), 294–307. ",
      url: "https://doi.org/10.1080/01944363.2024.2355305",
    },
    {
      text: "van Heyningen, E. (2021). ",
      journal: "District Six: Memories, Thoughts and Images",
      details: ".",
    },
    {
      text: "Zadeh, L. A. (1965). Fuzzy sets. ",
      journal: "Information and Control",
      details: ", 8(3), 338–353. ",
      url: "https://doi.org/10.1016/S0019-9958(65)90241-X",
    },
    {
      text: "Zhang, W., Zhao, R., Yao, Y., Wan, Y., Wu, P., Li, J., Li, Y., & Zhang, Y. (2025). Multi-resolution SAR and optical remote sensing image registration methods: A review, datasets, and future perspectives. ",
      url: "https://arxiv.org/abs/2502.01002",
    },
  ];

  return (
    <Slide>
      <h2 className="section-title">Bibliography</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr", // Two columns for better fit
          gap: "1.5rem 2rem",
          marginTop: "2rem",
          alignItems: "start",
        }}
      >
        {references.map((ref, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            style={{
              fontSize: "0.95rem",
              lineHeight: "1.5",
              color: "var(--text-main)",
              paddingLeft: "1.5rem",
              textIndent: "-1.5rem", // Creates the academic hanging indent
            }}
          >
            <span>{ref.text}</span>
            {ref.journal && <em>{ref.journal}</em>}
            {ref.details && <span>{ref.details}</span>}
            {ref.url && (
              <a
                href={ref.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: "var(--accent)",
                  textDecoration: "none",
                  wordBreak: "break-all", // Prevents long URLs from breaking the layout
                }}
              >
                {ref.url}
              </a>
            )}
          </motion.div>
        ))}
      </div>

      {/* Optional: Small footer note */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.5 }}
        style={{
          marginTop: "3rem",
          fontSize: "0.85rem",
          color: "var(--text-muted)",
          textAlign: "center",
          fontStyle: "italic",
        }}
      >
        A full list of references, including methodology and technical papers,
        is available in the accompanying thesis document.
      </motion.p>
    </Slide>
  );
};
