import React, { type ReactNode } from "react";
import { motion, useInView } from "framer-motion";

interface SlideProps {
  children: ReactNode;
  id?: string;
}

export const Slide: React.FC<SlideProps> = ({ children, id }) => {
  // We use a ref to detect when this specific slide is in view
  const ref = React.useRef(null);
  // Trigger animation when 30% of the slide is visible
  const isInView = useInView(ref, { amount: 0.3, once: false });
  /*
  const variants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut", staggerChildren: 0.2 },
    },
  };*/

  return (
    <div className="slide-wrapper" ref={ref}>
      <motion.div
        className="slide-content"
        id={id}
        initial="hidden"
        animate={isInView ? "visible" : "hidden"}
      >
        {children}
      </motion.div>
    </div>
  );
};
