import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { AskAISection } from "@/components/chat/AskAISection";

export default function ChatPage() {
  return (
    <>
      <Navbar />
      <AskAISection />
      <Footer />
    </>
  );
}
