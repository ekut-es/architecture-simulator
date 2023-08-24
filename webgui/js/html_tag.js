// used for template strings so that the extension knows it's a html string. This function itself doesn't do anything except string interpolation I think.
const html = (strings, ...values) => String.raw({ raw: strings }, ...values);
