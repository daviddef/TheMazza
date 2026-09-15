/* The surnames this archive holds, ranked, for the front page. The full
   descent test lives on /marriages/; what a chart needs is a name and a
   number, and taking those from the same file keeps the two honest. */
import families from "../data/families.json";
export const chartGroups = [{
  key: "all", label: "Every surname the archive holds",
  families: families.filter((f) => f.n > 0)
    .sort((a, b) => b.n - a.n)
    .map((f) => ({ surname: f.surname, n: f.n })),
}];
