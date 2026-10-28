import { motion } from "framer-motion";
import { Slide } from "../components/Slide";

interface SlidePoemProps {
  step?: number;
}

const STANZAS = [
  <>
    I could have sworn I used to know this place right here
    <br /> I've forgotten my mother tongue <br />
    It's happened to us both <br /> We speak in a chorus of black box models
    growing larger
    <br /> and consuming more
    <br /> I don't know how to understand what's around
    <br />
    like a distorted lens has been placed over each eye
  </>,
  <>
    Won't you plan a place for me <br />
    and plan a place for you too?
  </>,
  <>
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
