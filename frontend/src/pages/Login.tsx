import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { readableError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

const loginSchema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
});
type LoginFields = z.infer<typeof loginSchema>;

export function Login() {
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
      await login(values.email, values.password);
      navigate("/", { replace: true });
    } catch (error) {
      setServerError(readableError(error));
    }
  }

  return (
    <main className="login-page">
      <div className="login-decoration decor-one" />
      <div className="login-decoration decor-two" />
      <section className="login-card">
        <div className="login-brand">
          <div className="brand-mark"><ShieldCheck size={22} /></div>
          <span>Northstar</span>
        </div>
        <div className="login-eyebrow">INSURANCE OPERATIONS</div>
        <h1>Good to see you.</h1>
        <p className="login-subtitle">Sign in to your secure claims workspace.</p>
        <form className="login-form" onSubmit={handleSubmit(submit)} noValidate>
          <label htmlFor="email">Work email</label>
          <input
            id="email"
            autoComplete="username"
            placeholder="you@company.com"
            type="email"
            {...register("email")}
          />
          {errors.email && <span className="field-error">{errors.email.message}</span>}
          <label htmlFor="password">Password</label>
          <input
            id="password"
            autoComplete="current-password"
            placeholder="Enter your password"
            type="password"
            {...register("password")}
          />
          {errors.password && <span className="field-error">{errors.password.message}</span>}
          {serverError && <div className="form-alert" role="alert">{serverError}</div>}
          <button className="button button-primary login-submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in…" : "Sign in"}
            {!isSubmitting && <ArrowRight size={17} />}
          </button>
        </form>
        <div className="login-footnote"><span className="secure-dot" /> Protected with secure account access</div>
        <p className="login-account-help">Accounts are issued by your administrator. Contact them if you need access.</p>
      </section>
      <div className="login-bottom">A calmer view of every claim.</div>
    </main>
  );
}
