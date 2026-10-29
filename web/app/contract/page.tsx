import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { ContractRunner } from "../../components/ContractRunner";

export const metadata = { title: "Contract check | Dogwatch" };

export default function Contract() {
  return (
    <>
      <PageHead
        eyebrow="Contract check"
        title="Is Arjun ready"
        serif="for this contract?"
        lede="Enter a contract window. The Navigator compares every document with it, in code, and shows the arithmetic and the rule behind each answer."
      />
      <section className="wrap" data-shot="contract" style={{ paddingBottom: 64 }}>
        <GlowCard><ContractRunner showApproval /></GlowCard>
      </section>
    </>
  );
}
