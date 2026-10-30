import { motion } from "framer-motion";
import { Slide } from "../components/Slide";

interface SlidePoemProps {
  step?: number;
}

const STANZAS = [
  <>
    I used to know this place right here
    <br />
    We speak in a chorus of black box models
    <br />
    This is the complicated force they call a city
    <br />
    You have to see it to believe it
  </>,
];

export const SlidePoem = ({ step = 0 }: SlidePoemProps) => {
  return (
    <Slide>
      <div id="poem">
        {STANZAS.map((stanza, i) => (
          <motion.p
            key={i}
            initial={false}
            animate={{
              opacity: i > step ? 0 : i === step ? 1 : 0.45,
              y: i > step ? 20 : 0,
            }}
            transition={{ duration: 0.5 }}
          >
            {stanza}
          </motion.p>
        ))}
      </div>
    </Slide>
  );
};
