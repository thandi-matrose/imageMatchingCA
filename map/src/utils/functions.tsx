import type { ReactElement } from "react";

export function highlight(text: string, colour: string = "main"): ReactElement {
  return <span className={`highlight ${colour}`}>{text}</span>;
}
