import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { readableError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { CustomerRegistration, Role } from "../types";

const roles = [
  "CUSTOMER",
  "AGENT",
  "CLAIMS_OFFICER",
  "SURVEYOR",
  "FINANCE",
  "ADMIN",
  "MANAGER",
] as const satisfies readonly Role[];

const loginSchema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
  role: z.enum(roles, { error: "Select your role." }),
});

const registrationSchema = z.object({
  name: z.string().min(2, "Enter your full name.").max(100),
  email: z.email("Enter a valid email address."),
  password: z.string().min(12, "Use at least 12 characters.").max(128),
  phone: z.string().min(10, "Enter a phone number with at least 10 characters.").max(20),
  address: z.string().min(3, "Enter your address."),
});

type LoginFields = z.infer<typeof loginSchema>;
type RegistrationFields = z.infer<typeof registrationSchema>;

export function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  return (
    <main className="login-page">
      <div className="login-decoration decor-one" />
      <div className="login-decoration decor-two" />
      {isRegistering ? (
        <RegisterForm onSwitch={() => setIsRegistering(false)} />
      ) : (
        <SignInForm onSwitch={() => setIsRegistering(true)} />
      )}
      <div className="login-bottom">A calmer view of every claim.</div>
    </main>
  );
}

function LoginBrand() {
  return (
    <div className="login-brand">
      <div className="brand-mark"><ShieldCheck size={22} /></div>
      <span>claimcare-portal</span>
    </div>
  );
}

function SignInForm({ onSwitch }: { onSwitch: () => void }) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFields>({ resolver: zodResolver(loginSchema) });

  async function submit(values: LoginFields) {
    setServerError("");
    try {
      await login(values.email, values.password, values.role);
      navigate("/", { replace: true });
    } catch (error) {
      setServerError(readableError(error));
    }
  }

  return (
    <section className="login-card">
      <LoginBrand />
      <div className="login-eyebrow">INSURANCE OPERATIONS</div>
      <h1>Good to see you.</h1>
      <p className="login-subtitle">Sign in to your secure claims workspace.</p>
      <form className="login-form" onSubmit={handleSubmit(submit)} noValidate>
        <label htmlFor="role">Sign in as</label>
        <select id="role" {...register("role")} defaultValue="">
          <option value="" disabled>Select your role</option>
          {roles.map((role) => (
            <option key={role} value={role}>
              {role.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (character) => character.toUpperCase())}
            </option>
          ))}
        </select>
        {errors.role && <span className="field-error">{errors.role.message}</span>}
        <label htmlFor="email">Work email</label>
        <input id="email" autoComplete="username" placeholder="you@company.com" type="email" {...register("email")} />
        {errors.email && <span className="field-error">{errors.email.message}</span>}
        <label htmlFor="password">Password</label>
        <input id="password" autoComplete="current-password" placeholder="Enter your password" type="password" {...register("password")} />
        {errors.password && <span className="field-error">{errors.password.message}</span>}
        {serverError && <div className="form-alert" role="alert">{serverError}</div>}
        <button className="button button-primary login-submit" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Signing in…" : "Sign in"}
          {!isSubmitting && <ArrowRight size={17} />}
        </button>
      </form>
      <div className="login-footnote"><span className="secure-dot" /> Protected with secure account access</div>
      <p className="login-account-help">
        Need a customer account?{" "}
        <button className="auth-mode-toggle" onClick={onSwitch} type="button">Create one</button>
      </p>
    </section>
  );
}

function RegisterForm({ onSwitch }: { onSwitch: () => void }) {
  const { registerCustomer } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegistrationFields>({ resolver: zodResolver(registrationSchema) });

  async function submit(values: RegistrationFields) {
    setServerError("");
    try {
      const customer: CustomerRegistration = values;
      await registerCustomer(customer);
      navigate("/", { replace: true });
    } catch (error) {
      setServerError(readableError(error));
    }
  }

  return (
    <section className="login-card">
      <LoginBrand />
      <div className="login-eyebrow">CUSTOMER REGISTRATION</div>
      <h1>Create your account.</h1>
      <p className="login-subtitle">Your customer profile and secure login are created together.</p>
      <form className="login-form" onSubmit={handleSubmit(submit)} noValidate>
        <label htmlFor="name">Full name</label>
        <input id="name" autoComplete="name" {...register("name")} />
        {errors.name && <span className="field-error">{errors.name.message}</span>}
        <label htmlFor="register-email">Email</label>
        <input id="register-email" autoComplete="email" placeholder="you@example.com" type="email" {...register("email")} />
        {errors.email && <span className="field-error">{errors.email.message}</span>}
        <label htmlFor="register-password">Password</label>
        <input id="register-password" autoComplete="new-password" type="password" {...register("password")} />
        {errors.password && <span className="field-error">{errors.password.message}</span>}
        <label htmlFor="phone">Phone</label>
        <input id="phone" autoComplete="tel" type="tel" {...register("phone")} />
        {errors.phone && <span className="field-error">{errors.phone.message}</span>}
        <label htmlFor="address">Address</label>
        <input id="address" autoComplete="street-address" {...register("address")} />
        {errors.address && <span className="field-error">{errors.address.message}</span>}
        {serverError && <div className="form-alert" role="alert">{serverError}</div>}
        <button className="button button-primary login-submit" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Creating account…" : "Create customer account"}
          {!isSubmitting && <ArrowRight size={17} />}
        </button>
      </form>
      <div className="login-footnote"><span className="secure-dot" /> Customer accounts only</div>
      <p className="login-account-help">
        Already registered?{" "}
        <button className="auth-mode-toggle" onClick={onSwitch} type="button">Sign in</button>
      </p>
    </section>
  );
}
