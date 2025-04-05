import { fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:roles');
	const { data: roles } = await supabase.from('roles').select('*').order('name');

	depends('supabase:db:trading-points');
	const { data: points } = await supabase.from('trading_points').select('*').order('name');

	return { roles: roles ?? [], points: points ?? [] };
};

export const actions = {
	add: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		console.log(formData);

		const first_name = formData.get('first_name');
		const last_name = formData.get('last_name');
		const email = formData.get('email');
		const role = formData.get('role');
		const trading_point = formData.get('trading_point');

		if (!first_name) {
			return fail(400, { first_name, missing: true });
		}

		if (!last_name) {
			return fail(400, { last_name, missing: true });
		}

		if (!email) {
			return fail(400, { email, missing: true });
		}

		if (!role) {
			return fail(400, { role, missing: true });
		}

		if (!trading_point) {
			return fail(400, { trading_point, missing: true });
		}
	}
};
