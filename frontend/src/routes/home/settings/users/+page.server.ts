import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:staff');
	const { data: staff } = await supabase
		.from('staff')
		.select('*,roles(name),trading_points(*)')
		.order('first_name');
	return { staff: staff ?? [] };
};

export const actions = {
	delete: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		const id = formData.get('id');
		const { error } = await supabase.from('staff').delete().eq('id', id);
		if (error) {
			return { success: false, message: error.message };
		} else {
			return { success: true, message: 'deleted' };
		}
	}
};
