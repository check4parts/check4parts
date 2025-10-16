import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { signUpNewUser } from '$lib/utils/signUpNewUser';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:roles');
	const { data: roles } = await supabase.from('roles').select('*').order('name');

	depends('supabase:db:trading-points');
	const { data: points } = await supabase.from('trading_points').select('*').order('name');

	return { roles: roles ?? [], points: points ?? [] };
};

export const actions: Actions = {
	add: async ({ request, locals: { supabase } }) => {
		const form_data = await request.formData();

		const first_name = form_data.get('first_name')?.toString();
		const last_name = form_data.get('last_name')?.toString();
		const middle_name = form_data.get('middle_name')?.toString();
		const phone_number = form_data.get('phone')?.toString();
		const email = form_data.get('email')?.toString();
		const role = form_data.get('role')?.toString();
		const trading_point = form_data.get('trading_point')?.toString();
		const password = form_data.get('password')?.toString();

		if (
			!first_name ||
			!last_name ||
			!email ||
			!role ||
			!trading_point ||
			!password ||
			!middle_name
		) {
			return fail(400, { missing: true });
		}

		const { data, error } = await signUpNewUser(email, password);

		if (error) {
			return fail(400, { error: error.code });
		}

		if (!data?.user?.id) {
			return fail(500, { error: 'User creation failed to return user ID' });
		}

		const { data: staff, error: staffError } = await supabase
			.from('staff')
			.insert([
				{
					first_name,
					last_name,
					middle_name,
					email,
					phone_number,
					role_id: role,
					trading_point_id: trading_point,
					user_id: data.user.id
				}
			])
			.select('*')
			.single();

		if (staffError) {
			console.error('Staff insert error:', staffError);
			return fail(500, { error: staffError });
		}

		return {
			success: true,
			id: staff!.id,
			first_name: staff!.first_name,
			last_name: staff!.last_name,
			middle_name: staff!.middle_name,
			email: staff!.email,
			phone_number: staff!.phone_number,
			role: staff!.role_id,
			trading_point: staff!.trading_point_id
		};
	}
};
