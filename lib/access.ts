export function signUpSuccessMessage(hasSession: boolean): string {
  return hasSession
    ? "Account created. You’re signed in."
    : "Account created. Confirm your email, then sign in. Only approved emails can access Role Radar.";
}

export function accessDeniedMessage(email: string): string {
  return `${email} is not approved for Role Radar.`;
}
