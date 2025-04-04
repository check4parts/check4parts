import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase }, params }) => {
	depends('supabase:db:staff');
	const userId = params.id;
	const { data: user , error } = await supabase
		.from('staff')
		.select('*,roles(name),trading_points(*)')
		.eq('id', userId);

	if (error) {
		return { user: {} };
	}
	return { user: user ?? {} };
};
