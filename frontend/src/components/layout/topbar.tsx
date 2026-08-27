"use client";

import { Bell, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function Topbar() {
  return (
    <header className="flex h-14 items-center gap-4 border-b bg-card px-4">
      <div className="flex-1 flex items-center gap-2 rounded-md bg-muted px-3 py-1.5">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search evaluations, traces..."
          className="border-0 bg-transparent p-0 text-sm focus-visible:ring-0"
        />
      </div>
      <Button variant="ghost" size="icon">
        <Bell className="h-5 w-5" />
      </Button>
      <Avatar className="h-8 w-8">
        <AvatarFallback>SA</AvatarFallback>
      </Avatar>
    </header>
  );
}
