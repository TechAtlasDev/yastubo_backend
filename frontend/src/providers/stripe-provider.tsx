"use client";

import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import React, { useState, useEffect } from "react";

// In production, this should be an environment variable
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "pk_test_sample");

export function StripeProvider({ children }: { children: React.ReactNode }) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);

  // Function to wrap/reset Elements with specific options like clientSecret
  const wrapElements = (options: any) => {
    return (
      <Elements stripe={stripePromise} options={options}>
        {children}
      </Elements>
    );
  };

  return (
    <Elements stripe={stripePromise}>
      {children}
    </Elements>
  );
}
