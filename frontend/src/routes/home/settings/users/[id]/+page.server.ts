import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase }, params }) => {
	depends('supabase:db:staff');
	const userId = params.id;
	const { data: user } = await supabase
		.from('staff')
		.select('*,roles(name),trading_points(*)')
		.eq('id', userId)
		.single();

	depends('supabase:db:roles');
	const { data: roles } = await supabase.from('roles').select('*').order('name');

	depends('supabase:db:trading-points');
	const { data: points } = await supabase.from('trading_points').select('*').order('name');
	return { user: user ?? {}, roles: roles ?? [], points: points ?? [] };
};

export const actions = {
	edit: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		const id = formData.get('id')?.toString();
		const first_name = formData.get('first_name')?.toString();
		const last_name = formData.get('last_name')?.toString();
		const middle_name = formData.get('middle_name')?.toString();
		const phone_number = formData.get('phone')?.toString();
		const role = formData.get('role')?.toString();
		const trading_point = formData.get('trading_point')?.toString();

		console.log({ role, trading_point });

		const { error } = await supabase
			.from('staff')
			.update({
				first_name: first_name,
				last_name: last_name,
				middle_name: middle_name,
				phone_number: phone_number,
				role_id: role || undefined,
				trading_point_id: trading_point || undefined
			})
			.eq('id', id);

		if (error) {
			console.log(error);
			return { success: false, message: error.message };
		} else {
			console.log('updated', id);
			return { success: true, message: 'updated' };
		}
	}
};
