import { describe, expect, it } from "vitest";
import { accessDeniedMessage, signUpSuccessMessage } from "./access";

describe("signUpSuccessMessage", () => {
  it("does not ask for email confirmation when Supabase already created a session", () => {
    expect(signUpSuccessMessage(true)).toBe("Account created. You’re signed in.");
  });

  it("asks for email confirmation only when Supabase returns no session", () => {
    expect(signUpSuccessMessage(false)).toBe(
      "Account created. Confirm your email, then sign in. Only approved emails can access Role Radar.",
    );
  });
});

describe("accessDeniedMessage", () => {
  it("identifies a signed-in email that is not on the allowlist", () => {
    expect(accessDeniedMessage("blocked@example.com")).toBe(
      "blocked@example.com is not approved for Role Radar.",
    );
  });
});
