import { fail, redirect } from "@sveltejs/kit";

import type { Actions } from "./$types";

export const actions: Actions = {
  register: async ({ request, locals: { supabase } }) => {
    const formData = await request.formData();

    const first_name = formData.get("first_name")?.toString();
    const last_name = formData.get("last_name")?.toString();
    const middle_name = formData.get("middle_name")?.toString();
    const region = formData.get("region")?.toString();
    const city = formData.get("city")?.toString();
    const street = formData.get("street")?.toString();
    const phone = formData.get("phone")?.toString();
    const email = formData.get("email")?.toString();

    if (
      !first_name ||
      !last_name ||
      !email ||
      !middle_name ||
      !region ||
      !city ||
      !street ||
      !phone
    ) {
      console.log("missing", {
        first_name,
        last_name,
        email,
        middle_name,
        region,
        city,
        street,
        phone,
      });
      return fail(400, { missing: true });
    }

    const { error } = await supabase.from("companies_to_approve").insert([
      {
        first_name,
        last_name,
        middle_name,
        region,
        city,
        street,
        phone,
        email,
      },
    ]);

    if (error) {
      return fail(400, {
        message: error.message,
        code: error.code,
        form: {
          first_name,
          last_name,
          middle_name,
          region,
          city,
          street,
          phone,
          email,
        },
      });
    }
    return { success: true };
  },
};
