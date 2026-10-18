/* A count in words, for prose that must follow the data instead of being typed.
   Zero to twenty in words; anything larger as figures. */
const SMALL = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
  "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
  "nineteen", "twenty"];
export const words = (n) => (Number.isInteger(n) && n >= 0 && n <= 20 ? SMALL[n] : String(n));
export const Words = (n) => { const w = words(n); return w.charAt(0).toUpperCase() + w.slice(1); };
