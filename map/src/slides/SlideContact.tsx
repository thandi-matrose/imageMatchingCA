import React, { useState } from "react";
import { Slide } from "../components/Slide";
import { useForm, ValidationError } from "@formspree/react";

export const SlideContact = () => {
  const [state, handleSubmit] = useForm("mbgdvddn");

  // Local state for the form fields
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  return (
    <Slide>
      <h2 className="section-title">Any Questions?</h2>

      <div className="contact-grid">
        {/* Left Column: QR Code and Email */}
        <div className="contact-info">
          <div className="qr-placeholder">
            {/* TODO*/}
            <div
              style={{
                width: "200px",
                height: "200px",
                backgroundColor: "#e0e0e0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "8px",
                border: "2px dashed #999",
                color: "#666",
                fontSize: "0.9rem",
                textAlign: "center",
                padding: "1rem",
              }}
            >
              [Insert your SVG QR Code here]
            </div>
          </div>
          <div className="email-block">
            <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
              Or email me directly:
            </p>
            <a href="mailto:mtrtha003@myuct.ac.za">mtrtha003@myuct.ac.za</a>
          </div>
        </div>

        {/* Right Column: Contact Form */}
        <div className="contact-form-container">
          {state.succeeded ? (
            <div
              style={{
                padding: "2rem",
                background: "#e8f5e9",
                borderRadius: "8px",
                textAlign: "center",
                color: "#2e7d32",
              }}
            >
              <h3 style={{ fontFamily: "inherit", margin: 0 }}>Thank you!</h3>
              <p style={{ margin: "0.5rem 0 0 0" }}>
                Your message has been sent successfully.
              </p>
            </div>
          ) : (
            <form
              onSubmit={handleSubmit}
              style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
            >
              <div>
                <label
                  htmlFor="name"
                  style={{
                    display: "block",
                    marginBottom: "0.3rem",
                    fontSize: "0.9rem",
                    fontWeight: 600,
                  }}
                >
                  Name
                </label>
                <input
                  id="name"
                  type="text"
                  name="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  style={inputStyle}
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  style={{
                    display: "block",
                    marginBottom: "0.3rem",
                    fontSize: "0.9rem",
                    fontWeight: 600,
                  }}
                >
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={inputStyle}
                />
                <ValidationError
                  prefix="Email"
                  field="email"
                  errors={state.errors}
                />
              </div>

              <div>
                <label
                  htmlFor="message"
                  style={{
                    display: "block",
                    marginBottom: "0.3rem",
                    fontSize: "0.9rem",
                    fontWeight: 600,
                  }}
                >
                  Message
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  required
                  rows={5}
                  style={{ ...inputStyle, resize: "vertical" }}
                />
                <ValidationError
                  prefix="Message"
                  field="message"
                  errors={state.errors}
                />
              </div>

              <button
                type="submit"
                disabled={state.submitting}
                style={{
                  padding: "0.8rem 1.5rem",
                  background: "var(--accent)",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  fontSize: "1rem",
                  fontWeight: 600,
                  cursor: state.submitting ? "not-allowed" : "pointer",
                  opacity: state.submitting ? 0.7 : 1,
                  transition: "opacity 0.2s",
                }}
              >
                {state.submitting ? "Sending..." : "Send Message"}
              </button>
            </form>
          )}
        </div>
      </div>
    </Slide>
  );
};

// Simple inline style for inputs to keep the file self-contained
const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "0.8rem",
  borderRadius: "6px",
  border: "1px solid #ccc",
  fontSize: "1rem",
  fontFamily: "inherit",
  boxSizing: "border-box",
};
