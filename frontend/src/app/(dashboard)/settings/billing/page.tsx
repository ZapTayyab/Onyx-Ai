"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CreditCard, CheckCircle2, ArrowUpCircle, ExternalLink } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: ["5 evaluations/month", "3 agents", "Basic reports", "Community support"],
    current: true,
  },
  {
    name: "Pro",
    price: "$99",
    period: "/month",
    features: ["100 evaluations/month", "20 agents", "JUnit reports", "Email support", "API access"],
    current: false,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    features: ["Unlimited evaluations", "Unlimited agents", "SSO-ready (OIDC)", "Dedicated support", "SLA", "On-premise option"],
    current: false,
  },
];

export default function BillingPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground">Manage your subscription and billing information</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.current ? "border-primary" : ""}>
            <CardHeader>
              <CardTitle className="text-lg">{plan.name}</CardTitle>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className="text-sm text-muted-foreground">{plan.period}</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              {plan.current ? (
                <Badge variant="success" className="w-full justify-center">Current Plan</Badge>
              ) : (
                <Button variant="outline" className="w-full">
                  <ArrowUpCircle className="mr-2 h-4 w-4" />
                  {plan.name === "Enterprise" ? "Contact Sales" : "Upgrade"}
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <CreditCard className="h-5 w-5 text-muted-foreground" />
            <div>
              <CardTitle className="text-base">Payment Method</CardTitle>
              <CardDescription>Manage your payment information</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-14 rounded bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                VISA
              </div>
              <div>
                <p className="text-sm font-medium">Visa ending in 4242</p>
                <p className="text-xs text-muted-foreground">Expires 12/2028</p>
              </div>
            </div>
            <Button variant="outline" size="sm">
              <ExternalLink className="mr-2 h-4 w-4" /> Manage in Stripe
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
