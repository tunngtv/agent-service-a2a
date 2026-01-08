"use client";

import { Thread } from "@/components/assistant-ui/thread";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThreadListSidebar } from "@/components/assistant-ui/threadlist-sidebar";
import { ModelPicker } from "@/components/assistant-ui/model-picker";

export default function Page() {
  return (
    <SidebarProvider>
      <div className="flex h-dvh w-full pr-0.5">
        <ThreadListSidebar />
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger />
            {/* <Separator orientation="vertical" className="mr-2 h-4" /> */}
            <ModelPicker />
          </header>
          <div className="flex-1 overflow-hidden">
            <Thread />
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}