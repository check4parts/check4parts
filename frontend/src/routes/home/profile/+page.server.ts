import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabase } }) => {
  const { data: { user } } = await supabase.auth.getUser()
  const { data: staff } = await supabase
    .from('staff')
    .select('*,trading_points(*),roles(*)')
    .eq('user_id', user?.id)
    .single();

  const { data: points } = await supabase.from('trading_points').select('*').order('name');
  const { data: roles } = await supabase.from('roles').select('*').order('name');
  return {
    user: user ?? null,
    staff: staff ?? null,
    points: points ?? [],
    roles: roles ?? []
  }
};

export const actions = {
  editName: async ({ request, locals: { supabase } }) => {
    const form_data = await request.formData();
    const id = form_data.get('id')?.toString();
    const first_name = form_data.get('first_name')?.toString();
    const last_name = form_data.get('last_name')?.toString();
    const middle_name = form_data.get('middle_name')?.toString();
    const { error } = await supabase.from('staff').update({ first_name, last_name, middle_name }).eq('id', id);
    if (error) {
      return { success: false, message: error.message };
    } else {
      return { success: true, message: 'name_updated' };
    }
  },
  editContactInformation: async ({ request, locals: { supabase } }) => {
    const form_data = await request.formData();
    const id = form_data.get('id')?.toString();
    const phone_number = form_data.get('phone_number')?.toString();
    const email = form_data.get('email')?.toString();
    const trading_point = form_data.get('trading_point')?.toString();
    const role = form_data.get('role')?.toString();

    const { error: staffError } = await supabase.from('staff').update({ phone_number, email, trading_point_id: trading_point, role_id: role }).eq('id', id);


    const { data, error: authError } = await supabase.auth.updateUser({
      email: email
    })

    if (staffError || authError) {
      return { success: false, message: staffError || authError };
    }
    return { success: true, message: 'contacts_updated', email_sent: !(data?.user?.email === email) };

  },
  resetPassword: async ({ locals: { supabase, session } }) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(session?.user?.email!);

    console.log(error, data)
    if (error) {
      return { success: false, message: JSON.stringify(error) };
    }
    return { success: true, message: 'password_updated', email_sent: true };
  }
}