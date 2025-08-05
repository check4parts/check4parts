import { fail } from "@sveltejs/kit";

export const actions = {
  changePassword: async ({ request, locals: { supabase } }) => {
    const formData = await request.formData();
    const password = formData.get('password')?.toString();
    const { data, error } = await supabase.auth.updateUser({
      password: password
    });
    
    if (error) {
      return fail(error.status!, {
        message: error.message,
        code: error.code,
        form: {
          password
        }
      });
    }

    console.log(data, error)

    return { success: true, code: 'password_updated' };
  }
}