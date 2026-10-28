import React from "react";
import { Slide } from "../components/Slide";
import { BlockMath, InlineMath } from "react-katex";
import { motion, AnimatePresence } from "framer-motion";

interface SlideTheoryProps {
  step?: number;
}

export const SlideTheory = ({ step = 0 }: SlideTheoryProps) => {
  return (
    <Slide id="theory">
      <h2 className="section-title">
        The <span className="robo">syCAMOR</span> Framework
      </h2>

      {/* Persistent Context */}
      <div id="theory-block" style={{ minHeight: "80px" }}>
        <AnimatePresence mode="wait">
          {step === 0 && (
            <motion.div
              key="step0"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <p>
                We start with the general definition of a Cellular Automaton
                (CA):
              </p>
            </motion.div>
          )}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <p>
                For syCAMOR, the initial state <InlineMath math="F_j(0)" /> is
                determined by a <strong>Seeding Rule</strong> using fuzzy
                feature memberships.
              </p>
            </motion.div>
          )}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <p>
                The transition rule <InlineMath math="T" /> is the{" "}
                <strong>Growing Rule</strong>, combining feature evidence with
                neighbourhood evidence.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Dynamic Equations */}
      <div style={{ position: "relative", minHeight: "400px" }}>
        <AnimatePresence mode="wait">
          {/* STEP 0: General CA */}
          {step === 0 && (
            <motion.div
              key="eq0"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              transition={{ duration: 0.4 }}
              className="math-block"
              style={{ textAlign: "center" }}
            >
              <div className="two-col">
                <div>
                  <img
                    src="figures/game_of_life.gif"
                    style={{ width: "100%" }}
                  />
                  <p>Conway's Game of Life</p>
                </div>
                <div>
                  <BlockMath math="CA \sim \{j, t, F_j(t), N_j(t), T\}" />
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "1rem",
                      marginTop: "2rem",
                      fontSize: "0.9rem",
                      textAlign: "left",
                    }}
                  >
                    <div>
                      <InlineMath math="j" /> : cell
                    </div>
                    <div>
                      <InlineMath math="t" /> : time step
                    </div>
                    <div>
                      <InlineMath math="F_j(t)" /> : cell state
                    </div>
                    <div>
                      <InlineMath math="N_j(t)" /> : neighbourhood
                    </div>
                    <div style={{ gridColumn: "span 2" }}>
                      <InlineMath math="T" /> : transition rules
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 1: Seeding */}
          {step === 1 && (
            <motion.div
              key="eq1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4 }}
            >
              <div className="math-block">
                <p
                  style={{
                    margin: "0 0 1rem 0",
                    fontSize: "1.1rem",
                    fontWeight: "bold",
                  }}
                >
                  Feature-Based Membership:
                </p>
                <BlockMath math="\mu^{(F)}_{j,c} = \left( \sum_{k=1}^{5} w(c,k) \cdot \big[\mu_{c,k}(x_{j,k})\big]^{p} \right)^{1/p}" />
              </div>

              <div className="math-block" style={{ marginTop: "1rem" }}>
                <p
                  style={{
                    margin: "0 0 1rem 0",
                    fontSize: "1.1rem",
                    fontWeight: "bold",
                  }}
                >
                  Seeding Rule (<InlineMath math="F_j(0)" />
                  ):
                </p>
                <BlockMath math="F_j(0) = \begin{cases} (\arg\max_c \mu^{(F)}_{j,c}, \max_c \mu^{(F)}_{j,c}) & \text{if } \max_c > \tau_{seed} \\ (0, 0) & \text{otherwise} \end{cases}" />
              </div>
            </motion.div>
          )}

          {/* STEP 2: Growing */}
          {step === 2 && (
            <motion.div
              key="eq2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4 }}
            >
              <div className="math-block">
                <p
                  style={{
                    margin: "0 0 1rem 0",
                    fontSize: "1.1rem",
                    fontWeight: "bold",
                  }}
                >
                  Combined Membership:
                </p>
                <BlockMath math="\mu_{j,c}(t+1) = \big(1 - \alpha(t)\big) \, \mu^{(F)}_{j,c} + \alpha(t) \, \mu^{(N)}_{j,c}" />
              </div>

              <div className="math-block" style={{ marginTop: "1rem" }}>
                <p
                  style={{
                    margin: "0 0 1rem 0",
                    fontSize: "1.1rem",
                    fontWeight: "bold",
                  }}
                >
                  State Update (<InlineMath math="F_j(t+1)" />
                  ):
                </p>
                <BlockMath math="F_j(t+1) = \begin{cases} F_j(t) & \text{if } \ell_j(t) \neq 0 \\ (\arg\max_c \mu_{j,c}(t+1), \max_c \mu_{j,c}(t+1)) & \text{if } \ell_j(t) = 0 \text{ and } \max_c > \tau \\ (0, 0) & \text{otherwise} \end{cases}" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Info */}
      <div
        style={{
          marginTop: "2rem",
          fontSize: "0.9rem",
          color: "var(--text-muted)",
        }}
      >
        {step === 0 && "Click to see how syCAMOR defines the initial state."}
        {step === 1 && "Click to see how syCAMOR defines the transition rule."}
        {step === 2 && "The CA iterates this growing rule until convergence."}
      </div>
    </Slide>
  );
};
